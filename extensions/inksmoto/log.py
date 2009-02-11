import logging
from os.path import expanduser

LOGFILE = expanduser('~/svg2lvl.log')

try:
    # no log with python 2.3
    logging.basicConfig(filename = LOGFILE,
                        format   = '%(asctime)s %(levelname)s %(message)s',
                        level    = logging.INFO)
except Exception, e:
    pass

def eraseLogFile():
    f = open(LOGFILE, 'w')
    f.close()

def outMsg(msg):
    import sys
    logging.info(msg)
    sys.stderr.write(msg + '\n')
