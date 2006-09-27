from xmotoExtension import XmotoExtension

class AddWrecker(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelValue(self):
        return 'typeid=Wrecker'
    
    def getStyleChanges(self):
        return [('fill', 'gray')]

    def getLabelChanges(self):
        # previously not a particle source
        if not (self.label.has_key('typeid') and self.label['typeid'] == 'ParticleSource'):
                self.label.clear()

        changes = [('typeid', 'ParticleSource')]

        if self.options.type != '':
            particleType = self.options.type.capitalize()
            changes.append((['type', particleType]))
        
        return changes




e = AddWrecker()
e.affect()
