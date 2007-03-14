from xmotoExtension import XmotoExtension

class AddBlockInLayer(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--layer", type="int", dest="layer", 
                                     help="block layer")

    def getLabelChanges(self):
        changes = []

        # previously not a block. clear it's dictionnary
	# to make it a 'normal' block
        if self.label.has_key('typeid'):
            self.label.clear()

        if self.label.has_key('position'):
            if self.label['position'].has_key('background'):
                del self.label['position']['background']
            if self.label['position'].has_key('dynamic'):
                del self.label['position']['dynamic']

        changes.append(['position', {'layerid': self.options.layer,
                                     'islayer': "true"}])

        return changes

e = AddBlockInLayer()
e.affect()
