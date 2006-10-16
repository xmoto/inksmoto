from xmotoExtension import XmotoExtension

class ChangeBlockTexture(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--texture", type="string", dest="texture", 
                                     help="texture name")

    def getLabelChanges(self):
        # previously not a block
        if self.label.has_key('typeid'):
            self.label.clear()
            self.style.clear()    

        if self.options.texture != '':
            return [('usetexture', {'id':self.options.texture})]
        else:
            return []

    def getStyleChanges(self):
        # inkscape limitation -- you can't change <svg> and <defs> from an extension
        #patternId = self.addPattern(self.options.texture)
        #return [('fill', 'url(#%s)' % patternId)]
        return []

e = ChangeBlockTexture()
e.affect()
