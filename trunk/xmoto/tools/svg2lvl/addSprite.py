from xmotoExtension import XmotoExtension

class AddSprite(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--name", type="string", dest="name", 
                                     help="sprite name")
        self.OptionParser.add_option("--z", type="int", dest="z", 
                                     help="sprite z")

    def getChanges(self):
        changes = []

        # previously not a sprite
        if not (self.dic.has_key('typeid') and self.dic['typeid'] == 'Sprite'):
                self.dic.clear()

        changes.append(('typeid',     'Sprite'))
        changes.append(('usetexture', self.options.name))
        changes.append(('z',          self.options.z))

        return changes

e = AddSprite()
e.affect()
