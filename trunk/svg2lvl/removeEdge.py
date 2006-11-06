from xmotoExtension import XmotoExtension

class removeEdge(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        if self.label.has_key('edge'):
            del self.label['edge']

        return []

    def getStyleChanges(self):
        if self.label.has_key('typeid'):
            return []

        self.style.clear()
        if self.label.has_key('position'):
            if self.label['position'].has_key('dynamic'):
                fillColor = 'lightcoral'
            else:
                fillColor = 'darkkhaki'
        else:
            fillColor = 'mediumaquamarine'
        return [('fill', fillColor)]

e = removeEdge()
e.affect()
