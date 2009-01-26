import logging, log
from xmotoExtension import XmExt
from xmotoTools import getHomeDir
from svg2lvl import svg2lvl
from os.path import join, isfile
from os import execl, execlp
import os

class launchXmoto(XmExt):
    def __init__(self):
        XmExt.__init__(self)
        self.OptionParser.add_option("--xmoto",   type="string", dest="xmoto",   help="xmoto executable")
        self.OptionParser.add_option("--dummy",   type="string", dest="dummy",   help="dummy text")

    def effectHook(self):
        # check that the xmoto executable is present
        givenXmotoPresent = True
	xmotopath = self.options.xmoto
	logging.info("xmotopath=%s" % xmotopath)

        try:
            if not isfile(xmotopath):
                givenXmotoPresent = False
                logging.info("path[%s] is not a valid file" % xmotopath)
        except Exception, e:
            givenXmotoPresent = False
            logging.info("path[%s] is not a valid file.\n%s" % (xmotopath, e))

        # export in lvl
        lvlfileName = join(getHomeDir(), 'last.lvl')
        try:
            svg2lvl(self.args[-1], lvlfileName)
        except Exception, e:
            log.outMsg(str(e))
            return False

        if os.name == 'nt':
            lvlfileName = "\"" + lvlfileName + "\""
        params = ['xmoto', '--testTheme', '--fps', lvlfileName]
        # launch it in xmoto
        if givenXmotoPresent == True:
            logging.info("launching executable: [%s][%s]" % (xmotopath, lvlfileName))
            try:
                execl(xmotopath, *params)
            except Exception, e:
                log.outMsg("Cant execute %s.\n%s" % (xmotopath, e))
        else:
            try:
                execlp('xmoto', *params)
            except Exception, e:
                log.outMsg("The xmoto executable is present neither in the given location (%s) nor in the PATH.\n%s" % (xmotopath, e))

        return False

if __name__ == "__main__":
    e = launchXmoto()
    e.affect()
