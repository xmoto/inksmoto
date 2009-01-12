from singleton import Singleton
from factory import Factory
import converters
import logging, log

class Inksmoto:
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def convert(self, inFilename, inFormat, outFormat):
        try:
            inConverter  = Factory().createObject('%s_converter' % inFormat)
        except:
            raise Exception("There's no converter to handle %s file format" % inFormat)
        try:
            outConverter = Factory().createObject('%s_converter' % outFormat)
        except:
            raise Exception("There's no converter to handle %s file format" % outFormat)

        # test if the inData is a file name
        try:
            inFile = open(inFilename, 'rb')
        except:
            raise Exception("Can't open file to convert. %s" % inFilename)

        return outConverter.export(inConverter.import_(inFile))
