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

from inksmoto.xmotoExtensionTkinter import XmExtTkElement
from inksmoto.xmotoTools import createIfAbsent
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGui
from inksmoto.factory import Factory

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
                                       'self.particle',
                                       AvailableElements()['PARTICLESOURCES'][defaultParticle]['file'],
                                       defaultParticle,
                                       toDisplay='particlesources',
                                       callback=self.updateBitmap,
                                       buttonName='particle')

    def updateBitmap(self, imgName, buttonName):
        self.particle.update(imgName, AvailableElements()['PARTICLESOURCES'])

def run():
    ext = ChangeParticleSource()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
