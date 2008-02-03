from xmotoExtension import XmotoExtension
import logging, log

class AddEdge(XmotoExtension):
    def __init__(self):
	logging.info("addedge constructor")
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="upper texture name")
        self.OptionParser.add_option("--downtexture", type="string", dest="downtexture",
                                     help="down texture name")
        self.OptionParser.add_option("--update_upper", type="string", dest="update_upper",
                                     help="if true, update upper texture")
        self.OptionParser.add_option("--update_down",  type="string", dest="update_down",
                                     help="if true, update down texture")
        self.OptionParser.add_option("--edge_description", type="string",
                                     dest="edge_description", help="not used")

    def getLabelChanges(self):
        changes = []
        # previously not a block
        if self.label.has_key('typeid'):
            self.label.clear()

        if self.options.update_upper == 'true' and self.options.texture not in ['', None]:
            changes.append(['edge', {'texture':self.options.texture}])
        if self.options.update_down  == 'true' and self.options.downtexture not in ['', None]:
            changes.append(['edge', {'downtexture':self.options.downtexture}])

        return changes

e = AddEdge()
e.affect()
