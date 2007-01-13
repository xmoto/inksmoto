from xmotoExtension import XmotoExtension

class AddStrawberry(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=Strawberry'

e = AddStrawberry()
e.affect()
