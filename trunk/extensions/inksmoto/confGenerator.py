from os.path import join
from xmotoTools import getHomeDir, loadFile
from singleton import Singleton
import sys
import log, logging
import copy

class Conf:
    __metaclass__ = Singleton

    def __init__(self):
        self.read()

    def read(self):
        self.vars = loadFile('inksmoto_configuration.py')

    def __setitem__(self, var, value):
        self.vars[var] = value

    def __getitem__(self, var):
        return self.vars[var]

    def write(self):
        confFile = join(getHomeDir(), 'inksmoto_configuration.py')
        f = open(confFile, 'wb')
        for key, value in self.vars.iteritems():
            if type(value) == str:
                value = "'%s'" % value
            f.write('%s = %s\n' % (key, value))
        f.close()
