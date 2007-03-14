from xmotoExtension import XmotoExtension

class AddStaticBlockInLayer(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--doit", type="string", dest="doit", 
                                     help="do it")

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

        if self.options.doit == 'true':
            changes.append(['position', {'islayer': "true"}])
        else:
            if self.label.has_key('position'):
                if self.label['position'].has_key('islayer'):
                    del self.label['position']['islayer']

        return changes

e = AddStaticBlockInLayer()
e.affect()
