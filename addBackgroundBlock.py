from xmotoExtension import XmotoExtension

class AddBackgroundBlock(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getLabelChanges(self):
        changes = []
        # previously not a block
        if self.label.has_key('typeid'):
            self.label.clear()

        if self.options.texture != '':
            changes.append((['usetexture', self.options.texture]))
        
        if self.label.has_key('dynamic'):
            del self.label['dynamic']

        changes.append(('background', None))

        return changes

    def getStyleChanges(self):
        return [('fill', 'darkkhaki')]

e = AddBackgroundBlock()
e.affect()
