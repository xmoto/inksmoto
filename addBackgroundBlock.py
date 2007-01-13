from xmotoExtension import XmotoExtension

class AddBackgroundBlock(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string",
                                     dest="texture", help="texture name")

    def getLabelChanges(self):
        changes = []
        # previously not a block. clear it's dictionnary
	# to make it a 'normal' block
        if self.label.has_key('typeid'):
            self.label.clear()

	# update the texture
        if self.options.texture not in ['', None]:
            changes.append(['usetexture', {'id':self.options.texture}])

	# update the block background state
	changes.append(['position', {'background':'true'}])

        return changes

e = AddBackgroundBlock()
e.affect()
