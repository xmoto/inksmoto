from inksmoto import log
from inksmoto.xmotoExtension import XmExt
from inksmoto.confGenerator import Conf
from inksmoto.testsCreator import TestsCreator

class DisableTrace(XmExt):
    def effectHook(self):
        conf = Conf()

        if conf['enableRecording'] == False:
            log.outMsg("There's no recording session in progress.")
            return False

        testsCreator = TestsCreator()
        testsCreator.generateTests()

        conf['enableRecording'] = False
        conf['recordingSession'] =  ''
        conf.write()

        return False

def run():
    ext = DisableTrace()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
