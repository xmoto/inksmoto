from xmotoExtension import XmotoExtension

class AddWrecker(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=Wrecker'
    
e = AddWrecker()
e.affect()
