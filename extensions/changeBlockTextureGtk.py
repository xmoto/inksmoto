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
from inksmoto.xmotoTools import NOTSET_BITMAP, getExistingImageFullPath
from inksmoto.xmotoTools import getIfPresent, getValue
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk

TEXTURES = AvailableElements()['TEXTURES']
EDGETEXTURES = AvailableElements()['EDGETEXTURES']

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

        for tex in ['texture', 'upperEdge', 'downEdge']:
            imgName = self.get(tex+'Label').get_text()
            self.textureCallback(tex, imgName not in NOTSET_BITMAP)

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
            # if the scale/depth box is not checked, delete the associated scale
            for (var, default) in [('scale', self.defScale),
                                   ('depth', self.defDepth)]:
                boxName = '_%s_%s_box' % (prefix, var)
                boxWidget = self.get(boxName)
                scaleName = '%s_%s' % (prefix, var)
                if boxWidget.get_active() == False:
                    self.defVals.delWithoutExcept(self.comVals,
                                                  scaleName, 'edge')

        for texture, prefix in [('texture', 'u'), ('downtexture', 'd')]:
            # if the edge texture is not set, delete the other attributes
            (present, value) = getIfPresent(self.comVals, 'edge', texture)
            if value in NOTSET_BITMAP:
                self.defVals.delWithoutExcept(self.comVals, texture, 'edge')
                self.defVals.delWithoutExcept(self.comVals, prefix, 'edges')
                self.defVals.delWithoutExcept(self.comVals, prefix+'_scale',
                                              'edges')
                self.defVals.delWithoutExcept(self.comVals, prefix+'_depth',
                                              'edges')
                self.defVals.delWithoutExcept(self.comVals,
                                              '_'+prefix+'_scale_box', 'edges')
                self.defVals.delWithoutExcept(self.comVals,
                                              '_'+prefix+'_depth_box', 'edges')

        return self.comVals

    def getWidgetsInfos(self):
        return {'texture': WidgetInfos('usetexture', 'id', self.defBitmap),
                'color': WidgetInfos('usetexture', 'color', self.defColor),
                'scale': WidgetInfos('usetexture', 'scale', self.defScale),
                'upperEdge': WidgetInfos('edge', 'texture', self.defBitmap),
                'u_color': WidgetInfos('edges', 'u', self.defColor),
                'd_color': WidgetInfos('edges', 'd', self.defColor),
                'downEdge': WidgetInfos('edge', 'downtexture', self.defBitmap),
                'angle': WidgetInfos('edges', 'angle', self.defAngle),
                'u_scale': WidgetInfos('edges', 'u_scale', self.defScale),
                'u_depth': WidgetInfos('edges', 'u_depth', self.defDepth),
                'd_scale': WidgetInfos('edges', 'd_scale', self.defScale),
                'd_depth': WidgetInfos('edges', 'd_depth', self.defDepth),
                '_u_scale_box': WidgetInfos('edges', '_u_scale_box', False),
                '_u_depth_box': WidgetInfos('edges', '_u_depth_box', False),
                '_d_scale_box': WidgetInfos('edges', '_d_scale_box', False),
                '_d_depth_box': WidgetInfos('edges', '_d_depth_box', False)}

    def updateBitmap(self, widget):
        name = widget.get_name()
        isEdge = False
        if name == 'texture':
            bitmapDict = TEXTURES
            colorWidget = self.get('color')
        elif name == 'downEdge':
            bitmapDict = EDGETEXTURES
            colorWidget = self.get('d_color')
            (isEdge, prefix) = (True, 'd')
        elif name == 'upperEdge':
            bitmapDict = EDGETEXTURES
            colorWidget = self.get('u_color')
            (isEdge, prefix) = (True, 'u')

        imgName = xmGuiGtk.bitmapSelectWindow('Bitmap Selection',
                                              bitmapDict).run()

        if imgName is not None:
            xmGuiGtk.addImgToBtn(widget, self.get(name+'Label'),
                                 imgName, bitmapDict)
            xmGuiGtk.resetColor(colorWidget)
            self.textureCallback(name, imgName not in NOTSET_BITMAP)
            if isEdge == True:
                # set the scale and depth value from the ones in the theme
                scale = float(getValue(EDGETEXTURES, imgName,
                                       'scale', self.defScale))
                self.get(prefix+'_scale').set_value(scale)
                depth = float(getValue(EDGETEXTURES, imgName,
                                       'depth', self.defDepth))
                self.get(prefix+'_depth').set_value(depth)

    def boxCallback(self, box):
        boxName = box.get_name()
        scaleName = boxName[len('_'):-len('_box')]
        if box.get_active() == True:
            self.get(scaleName).show()
        else:
            self.get(scaleName).hide()

    def textureCallback(self, name, show):
        boxes = []
        if name == 'texture':
            color = 'color'
        elif name == 'downEdge':
            color = 'd_color'
            boxes = ['_d_scale_box', '_d_depth_box']
        elif name == 'upperEdge':
            color = 'u_color'
            boxes = ['_u_scale_box', '_u_depth_box']

        if show == True:
            self.get(color).show()
            self.get(color+'Label').show()
            for box in boxes:
                self.get(box).show()
                self.boxCallback(self.get(box))
        else:
            self.get(color).hide()
            self.get(color+'Label').hide()
            for box in boxes:
                self.get(box).hide()
                self.get(box[len('_'):-len('_box')]).hide()

def run():
    e = ChangeBlockTexture()
    e.affect()
    return e

if __name__ == "__main__":
    run()
