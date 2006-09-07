from xmotoExtension import XmotoExtension

class AddDynamicBlock(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getChanges(self):
        changes = []
        # previously not a block
        if self.dic.has_key('typeid'):
            self.dic.clear()

        if self.options.texture != '' and self.options.texture != 'default':
            changes.append((['usetexture', self.options.texture]))
        
        if self.dic.has_key('background'):
            del self.dic['background']

        changes.append(('dynamic', None))

        return changes

e = AddDynamicBlock()
e.affect()
