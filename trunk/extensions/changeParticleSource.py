from xmotoExtensionTkinter import XmotoExtTkElement, XmBitmap, XmLabel
from xmotoTools import createIfAbsent
from listAvailableElements import particleSources

class ChangeParticleSource(XmotoExtTkElement):
    def getUserChanges(self):
        self.commonValues = {}
        self.commonValues['typeid'] = 'ParticleSource'

        createIfAbsent(self.commonValues, 'param')
        self.setOrDelBitmap(self.commonValues, 'param', 'type', self.particle)

        return self.commonValues

    def createWindow(self):
        self.defineWindowHeader(title='')

        defaultParticle = self.getValue(self.commonValues, 'param',
                                        'type', default='Fire')
        XmLabel(self.frame, 'Particle source type:')
        self.particle = XmBitmap(self.frame,
                                 particleSources[defaultParticle]['file'],
                                 defaultParticle,
                                 self.particleSelectionWindow,
                                 buttonName='particle')

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.particle.update(imgName, particleSources)

def run():
    ext = ChangeParticleSource()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
