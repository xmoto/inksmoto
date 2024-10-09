#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from gi.repository import Gtk
from inksmoto import log
from inksmoto.xmExtGtk import XmExtGtk
from inksmoto import xmGuiGtk
from inksmoto.confGenerator import Conf
from inksmoto.xmotoTools import checkId, getHomeDir
from os.path import join, isdir

class EnableTrace(XmExtGtk):
    def __init__(self):
        super().__init__()

    def getWindowInfos(self):
        gladeFile = "enableTrace.glade"
        windowName = "enableTrace"
        return (gladeFile, windowName)

    def effect(self):
        self.createWindow(self.apply)
        self.get('sessionName').set_text(Conf()['recordingSession'])
        self.mainLoop()

    def getWidgetsInfos(self):
        pass

    def getSignals(self):
        return {}

    def apply(self, widget):
        xmGuiGtk.quit()
        conf = Conf()

        if conf['enableRecording'] and conf['recordingSession'] != '':
            log.outMsg("There's already a recording session in progress.")
            return

        sessionName = self.get('sessionName').get_text()

        if not checkId(sessionName):
            log.outMsg("Invalid session name")
            return

        if sessionName == '':
            log.outMsg("You have to set the session name")
            return

        sessionDir = join(getHomeDir(), 'cur_tests', sessionName)
        if isdir(sessionDir):
            log.outMsg(f"The session {sessionName} already exists")
            return

        conf['enableRecording'] = True
        conf['recordingSession'] = sessionName
        conf['currentTest'] = 0
        conf.write()

def run():
    ext = EnableTrace()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
