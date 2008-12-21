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
        except Exception, e:
            raise Exception("There's no converter to handle %s file format.\n%s" % (inFormat, e))
        try:
            outConverter = Factory().createObject('%s_converter' % outFormat)
        except Exception, e:
            raise Exception("There's no converter to handle %s file format.\n%s" % (outFormat, e))

        # test if the inData is a file name
        try:
            inFile = open(inFilename, 'rb')
        except Exception, e:
            raise Exception("Can't open file to convert: %s.\n%s" % (inFilename, e))

        return outConverter.export(inConverter.import_(inFile))
