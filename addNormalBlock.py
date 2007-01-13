from xmotoExtension import XmotoExtension

class AddNormalBlock(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getLabelChanges(self):
        changes = []
        # previously not a block
        if self.label.has_key('typeid'):
            self.label.clear()

        if self.options.texture != '':
            changes.append((['usetexture', self.options.texture]))
        
        if self.label.has_key('background'):
            del self.label['background']

        if self.label.has_key('dynamic'):
            del self.label['dynamic']

        return changes

    def getStyleChanges(self):
        return [('fill', 'mediumaquamarine')]

e = AddNormalBlock()
e.affect()
