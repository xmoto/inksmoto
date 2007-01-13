from xmotoExtension import XmotoExtension

class ChangeBlockTexture(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getLabelChanges(self):
        # previously not a block
        if self.label.has_key('typeid'):
            return []

        if self.options.texture != '':
            return [('usetexture', self.options.texture)]
        else:
            return []

e = ChangeBlockTexture()
e.affect()
