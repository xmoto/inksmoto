from xmotoExtension import XmotoExtension

class AddPhysics(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--grip", type="float", dest="grip", 
                                     help="grip value")

    def getLabelChanges(self):
        changes = []
        # previously not a block
        if self.label.has_key('typeid'):
            return []

	if self.options.grip != 0.0:
	    changes.append((['physics:grip', self.options.grip]))
        
        return changes

e = AddPhysics()
e.affect()
