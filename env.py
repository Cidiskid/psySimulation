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

    def getGrayCode(self, no):
        ret_code = []
        for i in range(self.N):
            ret_code.append(no % 2)
            no /= 2
        for i in range(self.N - 1):
            ret_code[i] = ret_code[i + 1] ^ ret_code[i]
        return ret_code

    def getValueFromStates(self, code):
        assert (len(code) == self.N)

        def code2int(t_code):
            return sum([t_code[i] * (2 ** int(i)) for i in range(len(t_code))])

        rtn_value = 0
        code_t = code + code
        for i in range(self.N):
            rtn_value += self.theta_func[i][code2int(code_t[i:i + self.K + 1])]
        return rtn_value / self.N

    def getValue(self, x):
        assert (type(x) == int)
        assert (0 <= x < 2 ** self.N)
        rtn_value = self.getValueFromStates(self.getGrayCode(x))
        logging.debug("nkmodel->getValue {} rtn={}".format(x, rtn_value))
        return rtn_value


class Env:
    def __init__(self, N, K, T):
        self.models = {"st": NKmodel(N,K),
                       "ed": NKmodel(N,K)}
        self.T = T

if (__name__ == "__main__"):
    import numpy as np
    all_config.load()
    moniter.LogInit()
    N = 20
    k = 3
    for i in range(10):
        nkmodel = NKmodel(N, k)
        point_pairs = []
        for j in range(2**N):
            point_pairs.append(nkmodel.getValue(j))
        npa = np.array(point_pairs)
        logging.info("N:%d, k:%d, mu=%0.4f, sigma=%0.4f"%(N,k,npa.mean(), npa.std()))
    moniter.DrawHist(point_pairs)