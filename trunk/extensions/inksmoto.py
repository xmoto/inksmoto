from singleton import Singleton
from factory import Factory
import converters
import logging, log

class Inksmoto:
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def convert(self, inData, inFormat, inIsFile, outFormat):
        try:
            inConverter  = Factory().createObject('%s_converter' % inFormat)
        except:
            raise Exception("There's no converter to handle %s file format" % inFormat)
        try:
            outConverter = Factory().createObject('%s_converter' % outFormat)
        except:
            raise Exception("There's no converter to handle %s file format" % outFormat)

        if inIsFile == True:
            inFile = open(inData, 'rb')
            inData = inFile.read()
            inFile.close()

        internalData = inConverter.import_(inData)
        outConverter.export(internalData)
        
            

        
