from xmotoExtension import XmotoExtension

class removeEdge(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        if self.label.has_key('edge'):
            del self.label['edge']

        return []

e = removeEdge()
e.affect()
