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
            self.label.clear()

        if self.options.texture not in ['', None]:
            changes.append(['usetexture', {'id':self.options.texture}])
        
        changes.append(['position', {'dynamic':'true'}])

        return changes

e = AddDynamicBlock()
e.affect()
