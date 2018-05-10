from config import all_config
import moniter
import logging
from copy import deepcopy

class Topomap:
    def __init__(self, config):
        self.N = config["N"]
        self.K = config["K"]
        self.minh = config["minh"]
        self.maxh = config["maxh"]
        self.M = config["M"]
        self.seed = None

    def gen_seed(self):
        pass

    def get_seed(self):
        if(self.seed is None):
        logging.error("Gen seed first")
        raise Exception("no seed")

    def set_seed(self, seed):
        self.seed = deepcopy(seed)

    def genMap(self):
        pass

class Env:
    def __init__(self):
        pass

if(__name__ == "__main__"):
    all_config.load()
    moniter.LogInit()
    tp=Topomap()