import os
from random import normalvariate as Norm
from random import uniform
from math import exp, pow, tanh, cos, pi
from copy import deepcopy
import logging

def clip(x,low, up):
    if(x > up):
        return  up
    if(x < low):
        return low
    return x

def softmaxM1(items):
    if (type(items) is list):
        sume = sum([exp(key) - 1 for key in items])
        return [(exp(key) - 1) / sume for key in items]
    else:
        sume = sum([exp(items[key]) - 1 for key in items])
        return {key: (exp(items[key]) - 1) / sume for key in items}


def random_choice(items):
    sume = sum([items[key] for key in items])
    rand = uniform(0, 1.0) * sume
    for key in items:
        if (rand <= items[key]):
            return key
        rand -= items[key]
    for key in items:
        return key


def max_choice(items):
    max_key = None
    for key in items:
        if (max_key is None or items[max_key] < items[key]):
            max_key = key
    return max_key


def init_global_arg():
    arg = {
        "Tf": 64,
        'T': 320,
        "Nagent": 5
    }
    return arg


def init_env_arg(global_arg):
    arg = {
        'N': 10,
        'K': 0,
        'T': global_arg['T']
    }
    arg['ESM'] = {
        "f-req": 0.75,
        "p-cplx": (lambda Tp: 1 - 0.75 ** (1.0 * global_arg['T'] / Tp) / (1 + exp(arg['K'] - 5))),
        "p-ugt": (1 - tanh(0.1 * (global_arg['Tf'] - 32))) * 0.5
    }
    return arg


def init_agent_arg(global_arg, env_arg):
    arg = {}
    arg['k'] = {
        "insight": clip(Norm(0.5, 0.2), 0.001, 0.999),
        "act": Norm(0.5, 0.1),
        "xplr": Norm(0.5, 0.3),
        "xplt": Norm(0.5, 0.3),
        "rmb": 8
    }
    arg["ob"] = (lambda x: Norm(x, 0.005 / arg['k']['insight']))
    arg['default'] = {
        "stage": {},
        "frame": {
            "SSM": {
                "rs-set": {},
                "rs-plan": [],
                'f-need': 0,
                's-sc': 0
            },
            'ACT': {
                'p': {
                    'zybkyb': 1,
                    'tscs': 0,
                    'jhzx': 0
                }
            }
        }
    }
    return arg


def init_stage_arg(global_arg, env_arg, agent_arg, last_arg, T):
    return {}


def init_frame_arg(global_arg, env_arg, agent_arg, stage_arg, last_arg, Tp, SSMfi):
    arg = {}
    arg['SSM'] = {
        "f-req": Norm(env_arg['ESM']['f-req'], 0.01 / agent_arg['k']['insight']),
        "p-cplx": Norm(env_arg['ESM']['p-cplx'](Tp), 0.01 / agent_arg['k']['insight']),
        "p-ugt": Norm(env_arg['ESM']['p-ugt'], 0.01 / agent_arg['k']['insight']),
        "rs-set": deepcopy(last_arg['SSM']['rs-set']),
        "rs-plan": deepcopy(last_arg['SSM']['rs-plan']),
        "s-sc": deepcopy(last_arg['SSM']['s-sc'])
    }
    SSMfneed_r = 1.0 / (1 + exp(5 * (SSMfi / arg['SSM']['f-req'] - 1)))
    SSMfneed_a = 0.5
    arg['SSM']['f-need'] = SSMfneed_a * last_arg['SSM']['f-need'] + (1 - SSMfneed_a) * SSMfneed_r

    f1 = 1 + 0.5 * tanh(5 * (arg['SSM']['f-need'] - 0.75)) \
         + 0.5 * tanh(5 * (agent_arg['k']['act'] - 0.5))
    g1 = 1 - 0.2 * tanh(5 * (arg['SSM']['p-cplx'] - 0.625))
    h1 = 1 + 0.1 * cos(pi * (arg['SSM']['p-ugt'] - 0.5))
    arg['PROC'] = {
        'a-m': f1 * g1 * h1,
        'a-th': 0.6
    }
    arg['PROC']['action'] = (Norm(arg['PROC']['a-m'] - arg['PROC']['a-th'], 0.1) > 0)

    arg['ACT'] = {
        'p': {},
        'zybkyb': {
            'n_near': env_arg['N'] // 2
        },
        'tscs': {
            'n_try': 7,
            'p_deep': 0.5
        },
        'jhzx': {}
    }
    zybkyb_a = 0.5
    arg['ACT']['p']['zybkyb'] = zybkyb_a * last_arg['ACT']['p']['zybkyb'] + (1 - zybkyb_a) * 0.5
    tscs_a = 0.5
    f2 = 1 - tanh(10 * (last_arg['SSM']['s-sc'] - 0.8 * arg['SSM']['f-req']))
    g2 = 1 + 0.2 * tanh(5 * (agent_arg['k']['xplr'] - 0.5))
    h2 = 1 + 0.1 * cos(pi * (arg['SSM']["p-ugt"] - 0.5))
    l2 = 1 + 0.2 * tanh(5 * (arg['SSM']['p-cplx'] - 0.5))
    arg['ACT']['p']['tscs'] = tscs_a * last_arg['ACT']['p']['tscs'] + (1 - tscs_a) * f2 * g2 * h2 * l2
    f3 = 1 + tanh(5 * (last_arg['SSM']['s-sc'] - 0.8 * arg['SSM']['f-req']))
    g3 = 1 + 0.2 * tanh(5 * (agent_arg['k']['xplt'] - 0.5))
    h3 = 2 + tanh(5 * (arg["SSM"]['p-ugt'] - 1))
    jhzx_a = 0.5
    arg['ACT']['p']['jhzx'] = jhzx_a * last_arg['ACT']['p']['jhzx'] + (1 - jhzx_a) * f3 * g3 * h3
    if (len(arg['SSM']['rs-plan']) < 1):
        arg['ACT']['p']['jhzx'] = 0

    arg['ACT']['choice'] = random_choice(softmaxM1(arg['ACT']['p']))

    return arg
