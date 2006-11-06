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
            self.style.clear()

        if self.options.texture not in ['', None]:
            changes.append(['edge', {'texture':self.options.texture}])

        return changes

    def getStyleChanges(self):
        if self.label.has_key('position'):
            if self.label['position'].has_key('dynamic'):
                fillColor = 'lightcoral'
            else:
                fillColor = 'darkkhaki'
        else:
            fillColor = 'mediumaquamarine'
        return [('stroke-width',    '1px'),   ('stroke-linecap', 'butt'),
                ('stroke-linejoin', 'miter'), ('stroke-opacity', '1'),
                ('stroke',          'lime'),  ('fill', fillColor)]
    
e = AddEdge()
e.affect()
