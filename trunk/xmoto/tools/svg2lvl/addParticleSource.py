from xmotoExtension import XmotoExtension

class AddParticleSource(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--type", type="string", dest="type", 
                                     help="particle source type")

    def getLabelChanges(self):
        # previously not a particle source
        if not (self.label.has_key('typeid') and self.label['typeid'] == 'ParticleSource'):
            self.label.clear()
            self.style.clear()

        changes = [('typeid', 'ParticleSource')]

        if self.options.type not in ['', None]:
            particleType = self.options.type.capitalize()
            changes.append(['param', {'type':particleType}])

        return changes

    def getStyleChanges(self):
        return [('fill', 'orange')]

e = AddParticleSource()
e.affect()
