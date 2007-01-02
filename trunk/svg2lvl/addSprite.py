from xmotoExtension import XmotoExtension
from listAvailableElements import sprites

class AddSprite(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--name", type="string", dest="name", 
                                     help="sprite name")
        self.OptionParser.add_option("--z", type="int", dest="z", 
                                     help="sprite z")

    def getLabelChanges(self):
        changes = []

        # previously not a sprite
        if not (self.label.has_key('typeid') and self.label['typeid'] == 'Sprite'):
            self.label.clear()

        changes.append(['typeid', 'Sprite'])
        changes.append(['param', {'name': self.options.name}])
        changes.append(['param', {'z':    self.options.z}])

        return changes

e = AddSprite()
e.affect()
