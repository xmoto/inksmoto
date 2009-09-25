#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from inksmoto import log
import logging
from inksmoto.xmotoExtension import XmExt
from inksmoto.xmotoTools import getHomeDir
from svg2lvl import svg2lvl
from os.path import join, isfile
import os
from traceback import format_exc

class LaunchXmoto(XmExt):
    def __init__(self):
        XmExt.__init__(self)
        self.OptionParser.add_option("--xmoto", type="string",
                                     dest="xmoto", help="xmoto executable")
        self.OptionParser.add_option("--dummy", type="string",
                                     dest="dummy", help="dummy")

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
            log.outMsg("%s\nSee log for more informations." % str(e))
            logging.warning(format_exc())
            return False

        if os.name == 'nt':
            lvlfileName = "\"" + lvlfileName + "\""
        params = ['xmoto', '--testTheme', '--fps', lvlfileName]
        # launch it in xmoto
        if givenXmotoPresent == True:
            logging.info("launching executable: [%s][%s]" % (xmotopath,
                                                             lvlfileName))
            try:
                os.execl(xmotopath, *params)
            except Exception, e:
                log.outMsg("Cant execute %s.\n%s" % (xmotopath, e))
        else:
            try:
                os.execlp('xmoto', *params)
            except Exception, e:
                log.outMsg("The xmoto executable is present neither in the \
given location (%s) nor in the PATH.\n%s" % (xmotopath, e))

        return False

def run():
    ext = LaunchXmoto()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
