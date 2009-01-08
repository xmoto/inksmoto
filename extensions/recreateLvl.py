import logging, log
from xmotoExtension import XmotoExtension
from xmotoTools import getHomeInkscapeExtensionsDir
from svg2lvl import svg2lvl
from os.path import join

class recreateLvl(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def effectHook(self):
        logging.info("recreate lvl file")
        lvlfileName = join(getHomeInkscapeExtensionsDir(), 'last.lvl')
        try:
            svg2lvl(self.args[-1], lvlfileName)
        except Exception, e:
            log.writeMessageToUser(str(e))
            return

        return False

if __name__ == "__main__":
    e = recreateLvl()
    e.affect()
