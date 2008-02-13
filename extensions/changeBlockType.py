from xmotoExtension import XmotoExtension

class ChangeBlockType(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string",
                                     dest="texture", help="texture name")
        self.OptionParser.add_option("--update", type="string",
                                     dest="update", help="if true, update the block texture")
        self.OptionParser.add_option("--background", type="string",
                                     dest="background", help="if true, convert into background block")
        self.OptionParser.add_option("--dynamic", type="string",
                                     dest="dynamic", help="if true, convert into dynamic block")
        self.OptionParser.add_option("--block_description", type="string",
                                     dest="block_description", help="")

    def getLabelChanges(self):
        changes = []
        # previously not a block. clear it's dictionnary
	# to make it a 'normal' block
        if self.label.has_key('typeid'):
            self.label.clear()

	# update the texture
        if self.options.update == 'true' and self.options.texture not in ['', None]:
            changes.append(['usetexture', {'id':self.options.texture}])

	# update the block background state
        if self.options.background == 'true':
            changes.append(['position', {'background':'true'}])
        else:
            if self.label.has_key('position'):
                if self.label['position'].has_key('background'):
                    del self.label['position']['background']
        if self.options.dynamic == 'true':
            changes.append(['position', {'dynamic':'true'}])
        else:
            if self.label.has_key('position'):
                if self.label['position'].has_key('dynamic'):
                    del self.label['position']['dynamic']

        return changes

e = ChangeBlockType()
e.affect()
