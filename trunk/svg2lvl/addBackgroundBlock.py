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
            self.style.clear()

	# update the texture
        if self.options.texture not in ['', None]:
            changes.append(['usetexture', {'id':self.options.texture}])

	# a background block can't be dynamic (may change in the future)
        if self.label.has_key('position'):
            if self.label['position'].has_key('dynamic'):
                del self.label['position']['dynamic']

	# update the block background state
	changes.append(['position', {'background':'true'}])

        return changes

    def getStyleChanges(self):
        if not self.label.has_key('edge'):
            self.style.clear()
        return [('fill', 'darkkhaki')]

e = AddBackgroundBlock()
e.affect()
