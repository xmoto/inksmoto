import logging, log
from xmotoExtension import XmExt
from xmotoTools import getHomeDir, getSystemDir
from os.path import join, isdir, normpath, exists
from os import mkdir
from shutil import copyfile

class InstallKeys(XmExt):
    def __init__(self):
        XmExt.__init__(self)

    def effectHook(self):
        logging.info("install default.xml in home directory")
        src  = join(getSystemDir(), 'xmoto_install', 'default.xml')
        if not exists(src):
            src = join(getHomeDir(), 'xmoto_install', 'default.xml')
            if not exists(src):
                log.outMsg("xmoto_install/default.xml is present neither in the\
 system directory nor in the home directory.")
                return False

        destDir = join(getHomeDir(), '..', 'keys')
        destDir = normpath(destDir)
        dest = join(destDir, 'default.xml')

        try:
            if not isdir(destDir):
                mkdir(destDir)
        except Exception, e:
            log.outMsg("Can't create the directory [%s]\n%s" % (destDir, e))
            return False

        try:
            copyfile(src, dest)
        except Exception, e:
            log.outMsg("Can't copy the shorcuts file \
from [%s] to [%s].\n%s" % (src, dest, e))
        else:
            log.outMsg("Inksmoto shorcuts installed.\n\
Restart Inkscape to activate them.")

        return False

def run():
    ext = InstallKeys()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()