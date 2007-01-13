import logging
from os.path import expanduser

logFile = expanduser('~/svg2lvl.log')

logging.basicConfig(level    = logging.INFO,
                    format   = '%(asctime)s %(levelname)s %(message)s',
                    filename = logFile)

def eraseLogFile():
    f = open(logFile, 'w')
    f.close()