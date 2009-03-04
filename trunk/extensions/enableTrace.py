import logging
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
