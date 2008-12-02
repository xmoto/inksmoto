import logging, log
from xmotoExtension import XmotoExtension, getInkscapeExtensionsDir
from svg2lvl import svg2lvl
from os.path import join

class recreateLvl(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    # we don't want to update the svg.
    def parse(self):
        pass
    def getposinlayer(self):
        pass
    def getselected(self):
        pass
    def getdocids(self):
        pass

    def effect(self):
        logging.info("recreate lvl file")
        lvlfileName = join(getInkscapeExtensionsDir(), 'last.lvl')
        try:
            svg2lvl(self.args[-1], lvlfileName)
        except Exception, e:
            log.writeMessageToUser(str(e))
            return

    def output(self):
        pass

e = recreateLvl()
e.affect()
