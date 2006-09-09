from xmotoExtension import XmotoExtension

class AddEdge(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getChanges(self):
        changes = []
        # previously not a block
        if self.dic.has_key('typeid'):
            self.dic.clear()

        if self.options.texture != '':
            changes.append((['edgeTexture', self.options.texture]))

        return changes

e = AddEdge()
e.affect()
