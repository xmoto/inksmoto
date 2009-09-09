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
from inksmoto.xmotoTools import NOTSET_BITMAP, getExistingImageFullPath
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk

class ChangeBlockTexture(XmExtGtkElement):
    def __init__(self):
        XmExtGtkElement.__init__(self)
        self.defScale = 1.0
        self.defDepth = 1.0
        self.defAngle = 270.0
        self.defMethod = 'angle'
        self.defColor = 255
        self.defBitmap = '_None_'
        self.namespacesInCommon = ['usetexture', 'edge', 'edges']
        self.namespacesToDelete = ['usetexture', 'edge', 'edges', 'typeid']

    def getWindowInfos(self):
        gladeFile = "changeBlockTexture.glade"
        windowName = "changeBlockTexture"
        return (gladeFile, windowName)

    def getSignals(self):
        # to update disabled buttons
        for boxName in ['_u_scale_box', '_u_depth_box',
                        '_d_scale_box', '_d_depth_box']:
            self.boxCallback(self.get(boxName))

        return {'on_texture_clicked': self.updateBitmap,
                'on_upperEdge_clicked': self.updateBitmap,
                'on_downEdge_clicked': self.updateBitmap,
                'on_u_scale_box_toggled': self.boxCallback,
                'on_u_depth_box_toggled': self.boxCallback,
                'on_d_scale_box_toggled': self.boxCallback,
                'on_d_depth_box_toggled': self.boxCallback}

    def getUserChanges(self):
        if self.get('textureLabel').get_text() in NOTSET_BITMAP:
            raise Exception('You have to give a texture to the block')

        for prefix in ['u', 'd']:
            for (var, default) in [('scale', self.defScale),
                                   ('depth', self.defDepth)]:
                boxName = '_%s_%s_box' % (prefix, var)
                boxWidget = self.get(boxName)
                scaleName = '%s_%s' % (prefix, var)
                if boxWidget.get_active() == False:
                    self.defVals.delWithoutExcept(self.comVals,
                                                  scaleName, 'edge')

        return self.comVals

    def getWidgetsInfos(self):
        return {'texture': ('usetexture', 'id', self.defBitmap, None),
                'color': ('usetexture', 'color', self.defColor, None),
                'scale': ('usetexture', 'scale', self.defScale, None),
                'upperEdge': ('edge', 'texture', self.defBitmap, None),
                'u_color': ('edges', 'u', self.defColor, None),
                'd_color': ('edges', 'd', self.defColor, None),
                'downEdge': ('edge', 'downtexture', self.defBitmap, None),
                'angle': ('edges', 'angle', self.defAngle, None),
                'u_scale': ('edges', 'u_scale', self.defScale, None),
                'u_depth': ('edges', 'u_depth', self.defDepth, None),
                'd_scale': ('edges', 'd_scale', self.defScale, None),
                'd_depth': ('edges', 'd_depth', self.defDepth, None),
                '_u_scale_box': ('edges', '_u_scale_box', False, None),
                '_u_depth_box': ('edges', '_u_depth_box', False, None),
                '_d_scale_box': ('edges', '_d_scale_box', False, None),
                '_d_depth_box': ('edges', '_d_depth_box', False, None)}

    def updateBitmap(self, widget):
        name = widget.get_name()
        if name == 'texture':
            bitmapDict = AvailableElements()['TEXTURES']
            colorWidget = self.get('color')
        elif name == 'downEdge':
            bitmapDict = AvailableElements()['EDGETEXTURES']
            colorWidget = self.get('d_color')
        elif name == 'upperEdge':
            bitmapDict = AvailableElements()['EDGETEXTURES']
            colorWidget = self.get('u_color')

        imgName = xmGuiGtk.bitmapSelectWindow('Bitmap Selection',
                                              bitmapDict).run()

        if imgName is not None:
            xmGuiGtk.addImgToBtn(widget, self.get(name+'Label'),
                                 imgName, bitmapDict)
            xmGuiGtk.resetColor(colorWidget)

    def boxCallback(self, box):
        boxName = box.get_name()
        scaleName = boxName[len('_'):-len('_box')]
        if box.get_active() == True:
            self.get(scaleName).show()
        else:
            self.get(scaleName).hide()

def run():
    e = ChangeBlockTexture()
    e.affect()
    return e

if __name__ == "__main__":
    run()
