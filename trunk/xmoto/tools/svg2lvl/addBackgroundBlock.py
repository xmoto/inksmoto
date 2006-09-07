from xmotoExtension import XmotoExtension

class AddBackgroundBlock(XmotoExtension):
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
        
        if self.dic.has_key('dynamic'):
            del self.dic['dynamic']

        changes.append(('background', None))

        return changes

e = AddBackgroundBlock()
e.affect()
