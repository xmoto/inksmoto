from xmotoExtension import XmotoExtension

class AddPlayerStart(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=PlayerStart'

e = AddPlayerStart()
e.affect()
