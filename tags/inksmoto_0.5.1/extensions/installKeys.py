import logging, log
from xmotoExtension import XmotoExtension
from xmotoTools import getHomeInkscapeExtensionsDir, getSystemInkscapeExtensionsDir
from os.path import join, isdir, normpath, exists
import os
from shutil import copyfile

class installKeys(XmotoExtension):
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
        logging.info("install default.xml in home directory")
        src  = join(getSystemInkscapeExtensionsDir(), 'xmoto_install', 'default.xml')
        if not exists(src):
            src = join(getHomeInkscapeExtensionsDir(), 'xmoto_install', 'default.xml')
            if not exists(src):
                log.writeMessageToUser("xmoto_install/default.xml is present neither in the system directory nor in the home directory.")
                return

        destDir = join(getHomeInkscapeExtensionsDir(), '..', 'keys')
        destDir = normpath(destDir)
        dest = join(destDir, 'default.xml')

        try:
            if not isdir(destDir):
                os.makedirs(destDir)
        except:
            log.writeMessageToUser("Can't create the directory [%s]" % destDir)
            return

        try:
            copyfile(src, dest)
        except:
            log.writeMessageToUser("Can't copy the shorcuts file from [%s] to [%s]." % (src, dest))
        else:
            log.writeMessageToUser("Inksmoto shorcuts installed.\nRestart Inkscape to activate them.")

    def output(self):
        pass

e = installKeys()
e.affect()
