from xmotoExtension import XmotoExtension
from listAvailableElements import sprites
import math

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

        changes.append(['position', {'layerid': self.options.layer,
                                     'islayer': "true"}])

        return changes

e = AddBlockInLayer()
e.affect()
