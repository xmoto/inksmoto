from xmotoExtension import XmotoExtension

class AddParticleSource(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--type", type="string", dest="type", 
                                     help="particle source type")

    def getChanges(self):
        # previously not a particle source
        if not (self.dic.has_key('typeid') and self.dic['typeid'] == 'ParticleSource'):
                self.dic.clear()

        changes = [('typeid', 'ParticleSource')]

        if self.options.type != '':
            particleType = self.options.type.capitalize()
            changes.append((['type', particleType]))
        
        return changes


e = AddParticleSource()
e.affect()
