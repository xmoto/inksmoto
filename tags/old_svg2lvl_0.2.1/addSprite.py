from xmotoExtension import XmotoExtension

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

        changes.append(('typeid',     'Sprite'))
        changes.append(('usetexture', self.options.name))
        changes.append(('z',          self.options.z))

        return changes

    def getStyleChanges(self):
        return [('fill', 'magenta')]

e = AddSprite()
e.affect()
