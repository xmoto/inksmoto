#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from inksmoto.xmExtGtk import XmExtGtkElement
from inksmoto.xmotoTools import getExistingImageFullPath
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk
from inksmoto.factory import Factory
import inksmoto.log, logging
PARTICLESOURCES = AvailableElements()['PARTICLESOURCES']

class ChangeParticleSource(XmExtGtkElement):
    def __init__(self):
        XmExtGtkElement.__init__(self)
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
        return {'particle': ('param', 'type', self.defParticle, None)}

    def getSignals(self):
        return {'on_particle_clicked': self.updateBitmap}

    def updateBitmap(self, widget):
        imgName = xmGuiGtk.bitmapSelectWindow('Particle Source Selection',
                                              PARTICLESOURCES).run()

        if imgName is not None:
            imgFile = PARTICLESOURCES[imgName]['file']
            imgFullFile = getExistingImageFullPath(imgFile)
            xmGuiGtk.addImageToButton(widget, imgFullFile)
            self.get('particleLabel').set_text(imgName)

def run():
    ext = ChangeParticleSource()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
