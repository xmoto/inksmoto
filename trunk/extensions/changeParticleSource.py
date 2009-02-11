from xmotoExtensionTkinter import XmExtTkElement
from xmotoTools import createIfAbsent
from listAvailableElements import PARTICLESOURCES
import xmGui
from factory import Factory

class ChangeParticleSource(XmExtTkElement):
    def getUserChanges(self):
        self.commonValues = {}
        self.commonValues['typeid'] = 'ParticleSource'

        createIfAbsent(self.commonValues, 'param')
        self.defaultValues.setOrDelBitmap(self.commonValues, 'param', 'type', self.particle)

        return self.commonValues

    def createWindow(self):
        f = Factory()
        xmGui.defineWindowHeader(title='')

        defaultParticle = self.defaultValues.get(self.commonValues, 'param',
                                                 'type', default='Fire')
        f.createObject('XmLabel', 'Particle source type:')
        self.particle = f.createObject('XmBitmap',
                                       PARTICLESOURCES[defaultParticle]['file'],
                                       defaultParticle,
                                       toDisplay='particlesources',
                                       callback=self.updateBitmap,
                                       buttonName='particle')

    def updateBitmap(self, imgName, buttonName):
        self.particle.update(imgName, PARTICLESOURCES)

def run():
    ext = ChangeParticleSource()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
