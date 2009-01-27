import sys
from xmotoExtension import XmExt
from xmotoTools import addHomeDirInSysPath, getValue
addHomeDirInSysPath()

class ShowInfo(XmExt):
    def getLabelChanges(self):
        objectType = getValue(self.label, 'typeid', default='block')

        # current id is set by applyOnElements
        infos = "%s is a %s\n" % (self._id, objectType)
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

        return {}

def run():
    ext = ShowInfo()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
