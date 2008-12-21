import logging
from   os.path import expanduser

logFile = expanduser('~/svg2lvl.log')

try:
    # no log with python 2.3
    logging.basicConfig(filename = logFile,
                        format   = '%(asctime)s %(levelname)s %(message)s',
                        level    = logging.INFO)
except Exception, e:
    pass

def eraseLogFile():
    f = open(logFile, 'w')
    f.close()

def writeMessageToUser(msg):
    import sys
    logging.info(msg)
    sys.stderr.write(msg + '\n')
