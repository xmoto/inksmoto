#!/bin/python
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

from inksmoto.xmExtGtk import XmExtGtkElement, WidgetInfos
from inksmoto.xmotoTools import delWithoutExcept

class ChangeBlock(XmExtGtkElement):
    def __init__(self):
        XmExtGtkElement.__init__(self)
        self.defGrip  = 20.0
        self.defMass  = 30.0
        self.defElasticity = 0.0
        self.defFriction = 0.5
        self.namespacesInCommon = ['position', 'physics']
        self.namespacesToDelete = ['position', 'physics', 'typeid']

    def getUserChanges(self):
        if 'position' in self.comVals:
            if 'physics' not in self.comVals['position']:
                for var in ['mass', 'elasticity', 'friction', 'infinitemass']:
                    self.defVals.delWithoutExcept(self.comVals, var, 'physics')

        return self.comVals

    def getWindowInfos(self):
        gladeFile = "changeBlock.glade"
        windowName = "changeBlock"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {'_usesmooth': WidgetInfos('position', '_usesmooth', False),
                '_smooth': WidgetInfos('position', '_smooth'),
                'background': WidgetInfos('position', 'background'),
                'dynamic': WidgetInfos('position', 'dynamic'),
                'physics': WidgetInfos('position', 'physics'),
                'grip': WidgetInfos('physics', 'grip', self.defGrip),
                'infinitemass':  WidgetInfos('physics', 'infinitemass'),
                'mass': WidgetInfos('physics', 'mass', self.defMass),
                'elasticity': WidgetInfos('physics', 'elasticity',
                                          self.defElasticity),
                'friction': WidgetInfos('physics', 'friction',
                                        self.defFriction)}

    def getSignals(self):
        self.physicsCallback()
        self.useSmoothCallback()

        return {'on_physics_toggled': self.physicsCallback,
                'on__usesmooth_toggled': self.useSmoothCallback}

    def physicsCallback(self, widget=None):
        if self.get('physics').get_active() == True:
            self.get('chipmunkFrame').show()
        else:
            self.get('chipmunkFrame').hide()

    def useSmoothCallback(self, widget=None):
        if self.get('_usesmooth').get_active() == True:
            self.get('_smooth').show()
        else:
            self.get('_smooth').hide()

def run():
    ext = ChangeBlock()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
