from xmotoExtension import XmotoExtension

class AddWrecker(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=Wrecker'
    
    def getStyleChanges(self):
        self.style.clear()
        return [('fill', 'gray')]

e = AddWrecker()
e.affect()
