from xmotoExtension import XmotoExtension

class AddNormalBlock(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getLabelChanges(self):
	# changing a block to 'normal' won't remove its edge
        changes = []
        # previously not a block
        if self.label.has_key('typeid'):
            self.label.clear()
            self.style.clear()

	# update the texture
        if self.options.texture != '':
            changes.append(['usetexture', {'id':self.options.texture}])
        
	if self.label.has_key('position'):
            if self.label['position'].has_key('background'):
                del self.label['position']['background']
            if self.label['position'].has_key('dynamic'):
                del self.label['position']['dynamic']

        return changes

    def getStyleChanges(self):
        if not self.label.has_key('edge'):
            self.style.clear()
        return [('fill', 'mediumaquamarine')]

e = AddNormalBlock()
e.affect()
