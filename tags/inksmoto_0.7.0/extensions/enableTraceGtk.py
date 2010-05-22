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
from inksmoto.xmExtGtk import XmExtGtk
from inksmoto import xmGuiGtk
from inksmoto.confGenerator import Conf
from inksmoto.xmotoTools import checkId, getHomeDir
from os.path import join, isdir

class EnableTrace(XmExtGtk):
    def getWindowInfos(self):
        gladeFile = "enableTrace.glade"
        windowName = "enableTrace"
        return (gladeFile, windowName)

    def effect(self):
        self.createWindow(self.apply)

        self.get('sessionName').set_text(Conf()['recordingSession'])

        self.mainLoop()

    def apply(self, widget):
        xmGuiGtk.quit()

        conf = Conf()

        if(conf['enableRecording'] == True
            and conf['recordingSession'] != ''):
            log.outMsg("There's already a recording session in progress.")
            return

        sessionName = self.get('sessionName').get_text()

        if checkId(sessionName) == False:
            log.outMsg("Invalid session name")
            return

        if sessionName == '':
            log.outMsg("You have to set the session name")
            return

        # check if that session already exists
        sessionDir = join(getHomeDir(), 'cur_tests', sessionName)
        if isdir(sessionDir):
            log.outMsg("The session %s already exists" % sessionName)
            return

        conf['enableRecording'] = True
        conf['recordingSession'] = "%s" % sessionName
        conf['currentTest'] = 0
        conf.write()

def run():
    ext = EnableTrace()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
