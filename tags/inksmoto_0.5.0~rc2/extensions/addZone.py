from xmotoExtension import XmotoExtension

class AddZone(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=Zone'

e = AddZone()
e.affect()
