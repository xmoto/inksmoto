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

from inksmoto import log 
import logging
from inksmoto.xmExtGtk import XmExtGtkElement, WidgetInfos
from inksmoto.xmotoTools import getExistingImageFullPath
from inksmoto.availableElements import AvailableElements
from math import radians, degrees
from inksmoto import xmGuiGtk
from inksmoto.factory import Factory
SPRITES = AvailableElements()['SPRITES']

class ChangeSprite(XmExtGtkElement):
    def __init__(self):
        XmExtGtkElement.__init__(self)
        self.defaultZ = -1
        self.defaultAngle = 0
        self.defaultScale = 1
        self.namespacesToDelete = 'all'

    def getUserChanges(self):
        self.comVals['typeid'] = 'Sprite'

        try:
            foo = self.comVals['param']['name']
        except:
            raise Exception("You have to set the sprite bitmap.")

        return self.comVals

    def getWindowInfos(self):
        gladeFile = "changeSprite.glade"
        windowName = "changeSprite"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {'sprite': WidgetInfos('param', 'name', '_None_'),
                'z': WidgetInfos('param', 'z', self.defaultZ),
                'angle': WidgetInfos('position', 'angle', self.defaultAngle,
                          (degrees, radians)),
                'reversed': WidgetInfos('position', 'reversed', False),
                'scale': WidgetInfos('size', 'scale', self.defaultScale)}

    def getSignals(self):
        return {'on_sprite_clicked': self.updateBitmap}

    def updateBitmap(self, widget):
        imgName = xmGuiGtk.bitmapSelectWindow('Sprite Selection',
                                              SPRITES).run()

        if imgName is not None:
            xmGuiGtk.addImgToBtn(widget, self.get('spriteLabel'),
                                 imgName, SPRITES)

def run():
    ext = ChangeSprite()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
