from config import all_config
import logging
import time

def LogInit():
    all_config.load()
    logging.basicConfig(level=logging._checkLevel(all_config['log']['filelv']),
                        format='%(asctime)s %(filename)s:%(lineno)d[%(levelname)s] %(message)s',
                        datefmt='%Y%d%m %H:%M:%S',
                        filename="./log/" + time.strftime("%Y%m%d-%H%M%S_") + all_config['log']['filepath'],
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging._checkLevel(all_config['log']['screanlv']))
    formatter = logging.Formatter('%(asctime)s %(funcName)s:%(lineno)d[%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
