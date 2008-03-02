from singleton  import Singleton
from factory    import Factory
import logging, log

class Converter:
    def __init__(self):
        pass

    def import_(self, inFile):
        pass

    def export(self):
        pass

class SvgConverter(Converter):
    def __init__(self):
        Converter.__init__()

    def import_(self, inFile):
        internalData = InternalFormat()
        parser.parse(svgFile, internalData)

    def export(self):
        pass

class LvlConverter(Converter):
    def __init__(self):
        Converter.__init__()

    def import_(self, inFile):
        pass

    def export(self):
        pass

def initModule():
    Factory().registerObject('svg_converter', SvgConverter)
    Factory().registerObject('lvl_converter', LvlConverter)

initModule()
