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
from inksmoto.xmotoTools import createIfAbsent, delWithoutExcept
from inksmoto import xmGui
from inksmoto.factory import Factory

class ChangeBlock(XmExtTkElement):
    def __init__(self):
        XmExtTkElement.__init__(self)
        self.defGrip  = 20.0
        self.defMass  = 30.0
        self.defElasticity = 0.0
        self.defFriction = 0.5
        self.namespacesInCommon = ['position', 'physics']

    def getUserChanges(self):
        delWithoutExcept(self.commonValues, 'position')
        delWithoutExcept(self.commonValues, 'physics')
        # if the block has been set as an entity
        delWithoutExcept(self.commonValues, 'typeid')

        # handle position
        createIfAbsent(self.commonValues, 'position')
        self.defaultValues.setOrDelBool(self.commonValues, 'position',
                                        self.background, 'background')
        self.defaultValues.setOrDelBool(self.commonValues, 'position',
                                        self.dynamic, 'dynamic')
        self.defaultValues.setOrDelBool(self.commonValues, 'position',
                                        self.physics, 'physics')

        createIfAbsent(self.commonValues, 'physics')
        self.commonValues['physics']['grip'] = self.grip.get()
        if 'physics' in self.commonValues['position']:
            self.defaultValues.setOrDelBool(self.commonValues, 'physics',
                                            self.infinity, 'infinitemass')
            self.commonValues['physics']['mass']       = self.mass.get()
            self.commonValues['physics']['elasticity'] = self.elasticity.get()
            self.commonValues['physics']['friction']   = self.friction.get()
        else:
            for var in ['mass', 'elasticity', 'friction']:
                delWithoutExcept(self.commonValues['physics'], var)

        return self.commonValues

    def createWindow(self):
        f = Factory()
        xmGui.defineWindowHeader(title='Block properties')

        # type
        f.createObject('XmTitle', "Type")
        f.createObject('XmLabel', "Uncheck all to convert into normal block.")
        value = self.defaultValues.get(self.commonValues, 'position', 'background')
        self.background = f.createObject('XmCheckbox',
                                         'self.background', value,
                                         text='Background block')
        value = self.defaultValues.get(self.commonValues, 'position', 'dynamic')
        self.dynamic = f.createObject('XmCheckbox',
                                      'self.dynamic', value,
                                      text='Dynamic block')
        value = self.defaultValues.get(self.commonValues, 'position', 'physics')
        self.physics = f.createObject('XmCheckbox',
                                      'self.physics', value,
                                      text='Physics block',
                                      command=self.physicsCallback)

        # physic
        f.createObject('XmTitle', "Ode Physic")
        f.createObject('XmLabel', "The grip with the bike wheels")
        value =  self.defaultValues.get(self.commonValues, 'physics',
                                        'grip', default=self.defGrip)
        self.grip = f.createObject('XmScale',
                                   'self.grip', value,
                                   label='Grip', from_=0, to=50,
                                   resolution=1, default=self.defGrip)

        f.createObject('XmTitle', "Chipmunk Physic")
        value = self.defaultValues.get(self.commonValues, 'physics',
                                       'infinitemass')
        self.infinity = f.createObject('XmCheckbox',
                                       'self.infinity', value,
                                       text='Infinite Mass')
        value = self.defaultValues.get(self.commonValues, 'physics',
                                       'mass', default=self.defMass)
        self.mass = f.createObject('XmScale',
                                   'self.mass', value,
                                   label='Mass', from_=1, to=1000,
                                   resolution=1, default=self.defMass)
        value = self.defaultValues.get(self.commonValues, 'physics',
                                       'elasticity', default=self.defElasticity)
        self.elasticity = f.createObject('XmScale',
                                         'self.elasticity', value,
                                         label='Elasticity', from_=0.0, to=1.0,
                                         resolution=0.1, default=self.defElasticity)
        value = self.defaultValues.get(self.commonValues, 'physics',
                                       'friction', default=self.defFriction)
        self.friction = f.createObject('XmScale',
                                       'self.friction', value,
                                       label='Friction', from_=0.0, to=1.0,
                                       resolution=0.1, default=self.defFriction)
        self.physicsCallback()

    def physicsCallback(self):
        if self.physics.get() == 1:
            self.infinity.show()
            self.mass.show()
            self.elasticity.show()
            self.friction.show()
        else:
            self.infinity.hide()
            self.mass.hide()
            self.elasticity.hide()
            self.friction.hide()

def run():
    ext = ChangeBlock()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
