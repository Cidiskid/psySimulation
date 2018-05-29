from config import all_config
import moniter
import logging
import random
from copy import deepcopy


class NKmodel:
    def __init__(self, n, k):
        assert (type(n) == int and type(k) == int)
        assert (0 <= k < n)
        logging.debug("Init NK model n=%d,k=%d" % (n, k))
        self.N = n
        self.K = k
        self.theta_func = self.genRandTheta(self.N, self.K)

    def genRandTheta(self, n, k):
        logging.debug("Init NK model -> genRandTheta")
        k_c_max = 2 ** (k + 1)
        logging.debug("genRandTheta: k_c_max %d*%d=%d" % (n, k_c_max, n * k_c_max))
        ret_map = []
        for i in range(n):
            ret_map.append([])
            for j in range(k_c_max):
                ret_map[i].append(random.random())
        return ret_map
    @staticmethod
    def getGrayCode(N, no):
        def XOR(a, b):
            return int(a+b-2*a*b)
        ret_code = []
        for i in range(N):
            ret_code.append(no % 2)
            no = no //  2
        for i in range(N - 1):
            ret_code[i] = XOR(ret_code[i + 1], ret_code[i])
        return ret_code

    @staticmethod
    def code2int(t_code):
        return int(sum([t_code[i] * (2 ** int(i)) for i in range(len(t_code))]))

    def getValueFromStates(self, code):
        assert (len(code) == self.N)
        rtn_value = 0
        code_t = code + code
        for i in range(self.N):
            rtn_value += self.theta_func[i][NKmodel.code2int(code_t[i:i + self.K + 1])]
        return rtn_value / self.N

    def getValue(self, x):
        assert (type(x) == int)
        assert (0 <= x < 2 ** self.N)
        rtn_value = self.getValueFromStates(NKmodel.getGrayCode(self.N, x))
        logging.debug("nkmodel->getValue {} rtn={}".format(x, rtn_value))
        return rtn_value


class Env:
    def __init__(self, arg):
        self.arg = arg
        self.N = arg['N']
        self.K = arg['K']
        self.models = {"st": NKmodel(self.N,self.K),
                       "ed": NKmodel(self.N,self.K)}
        self.T = arg['T']
        self.ESM = arg['ESM']

    def getValueFromStates(self, code, t):
        assert (len(code) == self.N)
        value_st = self.models["st"].getValueFromStates(code)
        value_ed = self.models["ed"].getValueFromStates(code)
        return value_st + (value_ed - value_st) * t / self.T

    def getValue(self, x, t):
        assert (type(x) == int)
        assert (0 <= x < 2**self.N)
        return self.getValueFromStates(NKmodel.getGrayCode(self.N, x), t)

    def getAllValue(self, t):
        return [self.getValue(i, t) for i in range(2**self.N)]

    def getAllPeakValue(self, t):
        peak_value = []
        for i in range(2**self.N):
            state = NKmodel.getGrayCode(self.N, i)
            state_value = self.getValueFromStates(state, t)

            flag = False
            for j in range(self.N):
                state_t = deepcopy(state)
                state_t[j] = 1 - int(state[j])
                if(state_value < self.getValueFromStates(state_t, t)):
                    flag = True
                    continue
            if(not flag):
                peak_value.append(state_value)
        logging.info("Ti: {}, peak num: {}".format(t, len(peak_value)))
        return peak_value

    @staticmethod
    def _getDistri(nums):
        all_value = sorted(nums)
        return {
            "max": all_value[-1],
            "min": all_value[0],
            "avg": sum(all_value)/len(all_value),
            "mid": all_value[len(all_value)//2],
            "p0.25": all_value[len(all_value)//4],
            "p0.75": all_value[len(all_value)*3//4],
        }

    def getModelDistri(self, t):
        return Env._getDistri(self.getAllValue(t))

    def getModelPeakDistri(self, t):
        return Env._getDistri(self.getAllPeakValue(t))


if (__name__ == "__main__"):
    import numpy as np
    all_config.load()
    moniter.LogInit()
    logging.info("Start")
    N = 12
    k = 10
    T = 100
    env = Env(N, k, T)
    for i in range(1):
        feat = []
        value = []
        for j in range(2**N):
            feat.append(NKmodel.getGrayCode(N, j))
            value.append(env.getValue(x=j, t=i))
#        moniter.DrawHist(point_pairs)
        moniter.Draw2DViaPCA(feat, value)
