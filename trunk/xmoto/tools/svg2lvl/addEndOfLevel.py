from xmotoExtension import XmotoExtension

class AddEndOfLevel(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=EndOfLevel'

    def getStyleChanges(self):
	self.style.clear()
        return [('fill', 'yellow')]

e = AddEndOfLevel()
e.affect()
