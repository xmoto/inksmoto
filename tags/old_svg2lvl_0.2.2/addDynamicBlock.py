from xmotoExtension import XmotoExtension

class AddDynamicBlock(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getLabelChanges(self):
        changes = []
        # previously not a block
        if self.label.has_key('typeid'):
            return []

        if self.options.texture != '':
            changes.append((['usetexture', self.options.texture]))
        
        if self.label.has_key('background'):
            del self.label['background']

        changes.append(('dynamic', None))

        return changes

    def getStyleChanges(self):
        return [('fill', 'lightcoral')]

e = AddDynamicBlock()
e.affect()
