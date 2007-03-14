from xmotoExtension import XmotoExtension

class RemoveBlockInLayer(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        changes = []

        if self.label.has_key('position'):
            if self.label['position'].has_key('layerid'):
                del self.label['position']['layerid']
            if self.label['position'].has_key('islayer'):
                del self.label['position']['islayer']

        return changes

e = RemoveBlockInLayer()
e.affect()
