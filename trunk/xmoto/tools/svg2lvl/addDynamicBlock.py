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
            self.style.clear()

        if self.options.texture not in ['', None]:
            changes.append(['usetexture', {'id':self.options.texture}])
        
	if self.label.has_key('position'):
            if self.label['position'].has_key('background'):
                del self.label['position']['background']

        changes.append(['position', {'dynamic':'true'}])

        return changes

    def getStyleChanges(self):
        if not self.label.has_key('edge'):
            self.style.clear()
        return [('fill', 'lightcoral')]

e = AddDynamicBlock()
e.affect()
