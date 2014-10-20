#coding: utf-8

import prerequisite
import sys,os
import common
import ColorStreamHandler


if __name__ == "__main__":
    print sys.path
    filename = os.path.abspath(__file__)
    print os.path.dirname(filename)
    print os.path.realpath('aa')

    filename = os.path.abspath(__file__)
    dirname = os.path.dirname(filename)
    utils = os.path.join(dirname,'utils')
    sys.path.insert(0,utils)

    logger = common.getLogger('sender')
    logger.warn('warnning...')
    logger.error('error!!!')
