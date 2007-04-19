from xmotoExtension import XmotoExtension

class AddDynamicBlock(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")
        self.OptionParser.add_option("--update", type="string",
                                     dest="update", help="if true, update the block texture")

    def getLabelChanges(self):
        changes = []
        # previously not a block
        if self.label.has_key('typeid'):
            self.label.clear()

        if self.options.update == 'true' and self.options.texture not in ['', None]:
            changes.append(['usetexture', {'id':self.options.texture}])
        
        changes.append(['position', {'dynamic':'true'}])

        return changes

e = AddDynamicBlock()
e.affect()
