from xmotoExtension import XmotoExtension

class AddZone(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=Zone'

    def getStyleChanges(self):
        self.style.clear()
        return [('fill', 'cyan')]

e = AddZone()
e.affect()
