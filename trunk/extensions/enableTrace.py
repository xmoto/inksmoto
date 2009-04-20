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
from inksmoto.xmotoExtensionTkinter import XmExtTk
from inksmoto import xmGui
from inksmoto.factory import Factory
from inksmoto.confGenerator import Conf
from inksmoto.xmotoTools import checkId, getHomeDir
from os.path import join, isdir

class EnableTrace(XmExtTk):
    def createWindow(self):
        f = Factory()

        xmGui.defineWindowHeader('Begin recording')
        self.sessionName = f.createObject('XmEntry', 'self.sessionName',
                                          Conf()['recordingSession'],
                                          label='Session name :')

    def apply(self):
        XmExtTk.apply(self)

        conf = Conf()

        if(conf['enableRecording'] == True
            and conf['recordingSession'] != ''):
            log.outMsg("There's already a recording session in progress.")
            return False

        sessionName = self.sessionName.get()

        if checkId(sessionName) == False:
            log.outMsg("Invalid session name")
            return False

        if sessionName == '':
            log.outMsg("You have to set the session name")
            return False

        # check if that session already exists
        sessionDir = join(getHomeDir(), 'cur_tests', sessionName)
        if isdir(sessionDir):
            log.outMsg("The session %s already exists" % sessionName)
            return False

        conf['enableRecording'] = True
        conf['recordingSession'] = "%s" % sessionName
        conf['currentTest'] = 0
        conf.write()

        return False

def run():
    ext = EnableTrace()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
