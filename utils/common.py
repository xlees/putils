# coding: utf-8

import sys,os
reload(sys).setdefaultencoding('utf-8')

from ConfigParser import ConfigParser
import inspect
import logging.config
import ColorStreamHandler
import cx_Oracle
import time


cur_dir = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])))
conf_dir = "conf"
conf_file = "cfg.ini"

logging_dir = "logs"
logging_file = "logging.conf"


def getConfFile():
    return os.path.join(cur_dir, conf_dir, conf_file)

def getLogFile():
    return os.path.join(cur_dir, conf_dir, logging_file)

def getConfig():
    config  = ConfigParser()
    config_file = os.path.join(cur_dir, conf_dir, conf_file)
    if not os.path.exists(config_file):
        raise IOError

    config.read(config_file)

    return config

def getTables():
    config  = ConfigParser()
    config_file = os.path.join(cur_dir, conf_dir, 'tables.ini')
    if not os.path.exists(config_file):
        raise IOError

    config.read(config_file)

    return config

def getLogger(loggerName):
    logFile = os.path.join(cur_dir, conf_dir, logging_file)
    if not os.path.exists(logFile):
        raise IOError

    try:
        logging.config.fileConfig(logFile)
    except IOError as e:
        if not os.path.exists(os.path.join(cur_dir,logging_dir)):
            print 'logging dir not exists, and i will create it.'
            os.mkdir(os.path.join(cur_dir,logging_dir))
            logging.config.fileConfig(logFile)

    return logging.getLogger(loggerName)

def getTfmOracle():
    conf = getConfig()
    logger = getLogger('')

    rinterval = conf.getint('common','reconnect_interval')
    max_times = conf.getint('common','max_retry_time')
    while max_times > 0:
        try:
            conn = cx_Oracle.connect(conf.get('db_tfm','user'),
                                     conf.get('db_tfm','pwd'),
                                     conf.get('db_tfm','cstring'))
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 12514:
                logger.error(u'%d: 无法连接到数据库！\n\t\t数据库信息：(%s, %s, %s)' 
                             % (error.code,
                                conf.get('db_tfm','user'),
                                conf.get('db_tfm','pwd'),
                                conf.get('db_tfm','cstring')))
                logger.warn(u'%d 秒后将重新进行连接...' % (rinterval))
                max_times -= 1
                time.sleep(rinterval)
                continue
            elif error.code == 12528 or error.code == 1033:
                logger.warn(e.message)
                time.sleep(5)
                continue
            else:
                logger.error(u'%d: 未知数据库错误！' % (error.code))
            raise Exception(e.message)
        break
    if max_times == 0:
        logger.warn(u'达到了最大尝试连接的次数，服务退出！' % (conf.getint('common','max_retry_time')))
        sys.exit(1)
    cursor = conn.cursor()

    return (conn,cursor)

def getItgsOracle():
    conf = getConfig()
    logger = getLogger('')

    rinterval = conf.getint('common','reconnect_interval')
    max_times = conf.getint('common','max_retry_time')
    while max_times > 0:
        try:
            conn = cx_Oracle.connect(conf.get('db_itgs','user'),
                                     conf.get('db_itgs','pwd'),
                                     conf.get('db_itgs','cstring'))
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 12514:
                logger.error(u'%d: 无法连接到数据库！\n\t\t数据库信息：(%s, %s, %s)' 
                             % (error.code,
                                conf.get('db_itgs','user'),
                                conf.get('db_itgs','pwd'),
                                conf.get('db_itgs','cstring')))
                logger.warn(u'%d 秒后将重新进行连接...' % (rinterval))
                max_times -= 1
                time.sleep(rinterval)
                continue
            elif error.code == 12528 or error.code == 1033:
                logger.warn(e.message)
                time.sleep(5)
                continue
            else:
                logger.error(u'%d: 未知数据库错误！' % (error.code))
            raise Exception(e.message)
        break
    if max_times == 0:
        logger.warn(u'达到了最大尝试连接的次数，服务退出！' % (conf.getint('common','max_retry_time')))
        sys.exit(1)
    cursor = conn.cursor()

    return (conn,cursor)

def closeOracle(conn,cursor):
    logger = getLogger('')
    try:
        cursor.close()
        conn.close()
    except cx_Oracle.DatabaseError:
        logger.error(u'关闭数据库错误！')
        pass

def toDict(cursor):
    """ 
    returns cx_Oracle rows as dicts 
    """
    desc = [r[0].lower() for r in cursor.description]
    for row in cursor:
        yield dict(zip(desc, row))


def spinningCursor():
    """ generator function """
    while True:
        for cursor in '|/-\\':
            yield cursor

def getMilliseonds(now):
    """
    convert a datetime object to millionseconds.
    """
    epoch = datetime.fromtimestamp(0)  # utcfromtimestamp
    delta = now - epoch
    total = (delta.days*86400 + delta.seconds + delta.microseconds/1e6)*1e3 # millionseconds

    return long(total)

def rejectOutliers(data, m=2.8):
    """
    Simple reject outlier function
    return: the index of non-outliers
    data: numpy array
    """
    if len(data) < 3:
        return np.where(data)
        
    d = np.abs(data - np.median(data)) # 用中位数来代替平均值
    mdev = np.median(d)
    s = d/mdev if mdev else 0
    return np.where(s<m)

def weight(size, alp=.5):
    """
    Generate the exponential weight.
    The generated weights are descending.
    """
    if alp<0 or alp>1:
        raise Exception(u'权重应在0到1之间！')
        
    if size<0:
        raise Exception(u'size应大于0！')
    elif size == 0:
        return []

    w = [0]*size
    w[0] = alp
    for i in range(1,size):
        w[i] = alp*pow(1-alp,i) # 权重从大到小
        
    return [i/sum(w) for i in w]
