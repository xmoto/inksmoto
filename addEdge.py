from xmotoExtension import XmotoExtension

class AddEdge(XmotoExtension):
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
            changes.append((['edgeTexture', self.options.texture]))

        return changes

    def getStyleChanges(self):
        return [('stroke-width',    '5px'),   ('stroke-linecap', 'butt'),
                ('stroke-linejoin', 'miter'), ('stroke-opacity', '1'),
                ('stroke',          'lime')]
    
e = AddEdge()
e.affect()
