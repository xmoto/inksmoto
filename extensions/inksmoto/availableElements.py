from singleton import Singleton
import log, logging
import sys
from xmotoTools import loadFile

class AvailableElements:
    __metaclass__ = Singleton

    def __init__(self):
        self.load()

    def load(self):
        self.vars = {}
        vars = loadFile('listAvailableElements.py')
        for var, value in vars.iteritems():
            self.vars[var.upper()] = value

    def __getitem__(self, var):
        return self.vars[var.upper()]
