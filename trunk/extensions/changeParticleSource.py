from xmotoExtensionTkinter import XmotoExtTkElement, XmotoBitmap
from xmotoTools import getValue, createIfAbsent, setOrDelBitmap
from svgnode import setNodeAsCircle
from listAvailableElements import particleSources
from inksmoto_configuration import defaultCollisionRadius, svg2lvlRatio
from inkex import addNS

class ChangeParticleSource(XmotoExtTkElement):
    def getUserChanges(self):
        self.commonValues = {}
        self.commonValues['typeid'] = 'ParticleSource'

        createIfAbsent(self.commonValues, 'param')
        setOrDelBitmap(self.commonValues['param'], 'type', self.particle)

        return self.commonValues

    def createWindow(self):
        self.defineWindowHeader(title='')

        defaultParticle = getValue(self.commonValues, 'param', 'type', default='Fire')
        self.defineLabel(self.frame, 'Particle source type:')
        self.particle = XmotoBitmap(self.frame, particleSources[defaultParticle]['file'], defaultParticle, self.particleSelectionWindow, buttonName='particle')

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.particle.update(imgName, particleSources)

e = ChangeParticleSource()
e.affect()
