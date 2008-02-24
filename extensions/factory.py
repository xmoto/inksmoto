from singleton import Singleton
import logging, log

class Factory:
    __metaclass__ = Singleton

    def __init__(self):
        self.objects = {}

    def registerObject(self, name, constructor):
        if name not in self.objects:
            self.objects[name] = constructor
            logging.debug('Factory::%s object added to the factory' % name)

    def createObject(self, name, *args, **keywords):
        if name in self.objects:
            return self.objects[name](*args, **keywords)
        else:
            logging.warning('Factory::%s object not present in the factory' % name)
            return None
        
