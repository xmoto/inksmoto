from singleton import Singleton
import logging, log

class Factory:
    __metaclass__ = Singleton

    def __init__(self):
        self.objects = {}

    def registerObject(self, name, constructor):
        if not self.objects.has_key(name):
            self.objects[name] = constructor
            logging.debug('Factory::%s object added to the factory' % name)

    def createObject(self, name, *args):
        if self.objects.has_key(name):
            return self.objects[name](*args)
        else:
            logging.warning('Factory::%s object not present in the factory' % name)
            return None
        