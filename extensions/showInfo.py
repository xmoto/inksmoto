from xmotoExtension import XmotoExtension
import sys
from xmotoTools import addHomeDirInSysPath
addHomeDirInSysPath()

class ShowInfo(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        if self.label.has_key('typeid'):
            objectType = self.label['typeid']
        else:
            objectType = 'block'

        infos = "%s is a %s\n" % (self.id, objectType)
        for key, value in self.label.iteritems():
            if type(value) == dict:
                if key == 'param':
                    for key, value in value.iteritems():
                        infos += "\tparam name=%s value=%s\n" % (key, value)
                else:
                    infos += "\t%s\n" % key
                    for key, value in value.iteritems():
                        infos += "\t\t%s=%s\n" % (key, value)

        sys.stderr.write(infos)

        return []

if __name__ == "__main__":
    e = ShowInfo()
    e.affect()
