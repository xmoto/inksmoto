#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from gi.repository import Gtk
from inksmoto.xmExtGtk import XmExtGtkElement, WidgetInfos
from inksmoto.xmotoTools import getExistingImageFullPath
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk
from inksmoto.factory import Factory
import inksmoto.log, logging

PARTICLESOURCES = AvailableElements()['PARTICLESOURCES']

class ChangeParticleSource(XmExtGtkElement):
    def __init__(self):
        super().__init__()
        self.comVals = {}
        self.defParticle = 'Fire'
        self.namespacesToDelete = 'all'

    def getUserChanges(self):
        self.comVals['typeid'] = 'ParticleSource'
        return self.comVals

    def getWindowInfos(self):
        gladeFile = "changeParticleSource.glade"
        windowName = "changeParticleSource"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {'particle': WidgetInfos('param', 'type', self.defParticle)}

    def getSignals(self):
        return {'on_particle_clicked': self.updateBitmap}

    def updateBitmap(self, widget):
        imgName = xmGuiGtk.BitmapSelectWindow('Particle Source Selection', PARTICLESOURCES).run()

        if imgName is not None:
            xmGuiGtk.addImgToBtn(widget, self.get('particleLabel'), imgName, PARTICLESOURCES)

def run():
    ext = ChangeParticleSource()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
