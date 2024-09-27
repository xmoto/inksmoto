#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from gi.repository import Gtk
from inksmoto.xmExtGtk import XmExtGtkElement, WidgetInfos
from inksmoto.xmotoTools import delWoExcept

class ChangeBlock(XmExtGtkElement):
    def __init__(self):
        super().__init__()
        self.defGrip = 20.0
        self.defMass = 30.0
        self.defElasticity = 0.0
        self.defFriction = 0.5
        self.namespacesInCommon = ['position', 'physics']
        self.namespacesToDelete = ['position', 'physics', 'typeid']

    def getUserChanges(self):
        if 'position' in self.comVals:
            if 'physics' not in self.comVals['position']:
                for var in ['mass', 'elasticity', 'friction', 'infinitemass']:
                    delWoExcept(self.comVals, var, 'physics')
        return self.comVals

    def getWindowInfos(self):
        gladeFile = "changeBlock.glade"
        windowName = "changeBlock"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {
            '_usesmooth': WidgetInfos('position', '_usesmooth', False),
            '_smooth': WidgetInfos('position', '_smooth'),
            'background': WidgetInfos('position', 'background'),
            'dynamic': WidgetInfos('position', 'dynamic'),
            'physics': WidgetInfos('position', 'physics'),
            'grip': WidgetInfos('physics', 'grip', self.defGrip),
            'infinitemass': WidgetInfos('physics', 'infinitemass'),
            'mass': WidgetInfos('physics', 'mass', self.defMass),
            'elasticity': WidgetInfos('physics', 'elasticity', self.defElasticity),
            'friction': WidgetInfos('physics', 'friction', self.defFriction)
        }

    def getSignals(self):
        self.physicsCallback()
        self.useSmoothCallback()

        return {
            'on_physics_toggled': self.physicsCallback,
            'on__usesmooth_toggled': self.useSmoothCallback
        }

    def physicsCallback(self, widget=None):
        if self.get('physics').get_active():
            self.get('chipmunkFrame').show()
        else:
            self.get('chipmunkFrame').hide()

    def useSmoothCallback(self, widget=None):
        if self.get('_usesmooth').get_active():
            self.get('_smooth').show()
        else:
            self.get('_smooth').hide()

def run():
    ext = ChangeBlock()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
