import logging, log
from xmotoExtension import XmExt
from xmotoTools import getHomeDir
from svg2lvl import svg2lvl
from os.path import join

class recreateLvl(XmExt):
    def __init__(self):
        XmExt.__init__(self)

    def effectHook(self):
        logging.info("recreate lvl file")
        lvlfileName = join(getHomeDir(), 'last.lvl')
        try:
            svg2lvl(self.args[-1], lvlfileName)
        except Exception, e:
            log.outMsg(str(e))

        return False

if __name__ == "__main__":
    e = recreateLvl()
    e.affect()
