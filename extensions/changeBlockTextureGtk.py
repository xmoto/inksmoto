#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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
        super().__init__()
        self.comVals = {}
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
        for boxName in ['_u_scale_box', '_u_depth_box', '_d_scale_box', '_d_depth_box']:
            self.boxCallback(self.get(boxName), boxName)

        for tex in ['texture', 'upperEdge', 'downEdge']:
            imgName = self.get(tex + 'Label').get_text()
            self.textureCallback(tex, imgName not in NOTSET_BITMAP)

        return {
            'on_texture_clicked': (self.updateBitmap, "texture"),
            'on_upperEdge_clicked': (self.updateBitmap, "upperEdge"),
            'on_downEdge_clicked': (self.updateBitmap, "downEdge"),
            'on_u_scale_box_toggled': (self.boxCallback, "_u_scale_box"),
            'on_u_depth_box_toggled': (self.boxCallback, "_u_depth_box"),
            'on_d_scale_box_toggled': (self.boxCallback, "_d_scale_box"),
            'on_d_depth_box_toggled': (self.boxCallback,  "_d_depth_box")
        }

    def getUserChanges(self):
        if self.get('textureLabel').get_text() in NOTSET_BITMAP:
            raise Exception('You have to give a texture to the block')

        for prefix in ['u', 'd']:
            for (var, default) in [('scale', self.defScale), ('depth', self.defDepth)]:
                boxName = f'_{prefix}_{var}_box'
                boxWidget = self.get(boxName)
                scaleName = f'{prefix}_{var}'
                if not boxWidget.get_active():
                    self.defVals.delWoExcept(self.comVals, scaleName, 'edge')

        for texture, prefix in [('texture', 'u'), ('downtexture', 'd')]:
            (present, value) = getIfPresent(self.comVals, 'edge', texture)
            if value in NOTSET_BITMAP:
                for key in [texture, f'{prefix}_r', f'{prefix}_g', f'{prefix}_b', f'{prefix}_a',
                            f'{prefix}_scale', f'{prefix}_depth', f'_{prefix}_scale_box', f'_{prefix}_depth_box']:
                    self.defVals.delWoExcept(self.comVals, key, 'edge')

        return self.comVals

    def getWidgetsInfos(self):
        return {
            'texture': WidgetInfos('usetexture', 'id', self.defBitmap),
            'color': WidgetInfos('usetexture', 'color', self.defColor),
            'scale': WidgetInfos('usetexture', 'scale', self.defScale),
            'upperEdge': WidgetInfos('edge', 'texture', self.defBitmap),
            'u_color': WidgetInfos('edge', 'u', self.defColor),
            'd_color': WidgetInfos('edge', 'd', self.defColor),
            'downEdge': WidgetInfos('edge', 'downtexture', self.defBitmap),
            'angle': WidgetInfos('edges', 'angle', self.defAngle),
            'u_scale': WidgetInfos('edge', 'u_scale', self.defScale),
            'u_depth': WidgetInfos('edge', 'u_depth', self.defDepth),
            'd_scale': WidgetInfos('edge', 'd_scale', self.defScale),
            'd_depth': WidgetInfos('edge', 'd_depth', self.defDepth),
            '_u_scale_box': WidgetInfos('edge', '_u_scale_box', False),
            '_u_depth_box': WidgetInfos('edge', '_u_depth_box', False),
            '_d_scale_box': WidgetInfos('edge', '_d_scale_box', False),
            '_d_depth_box': WidgetInfos('edge', '_d_depth_box', False)
        }

    def updateBitmap(self, widget, widget_id):  
        name = widget_id
        isEdge = False
        if name == 'texture':
            bitmapDict = TEXTURES
            colorWidget = self.get('color')
        elif name == 'downEdge':
            bitmapDict = EDGETEXTURES
            colorWidget = self.get('d_color')
            isEdge, prefix = True, 'd'
        elif name == 'upperEdge':
            bitmapDict = EDGETEXTURES
            colorWidget = self.get('u_color')
            isEdge, prefix = True, 'u'

        imgName = xmGuiGtk.BitmapSelectWindow('Bitmap Selection', bitmapDict).run()

        if imgName is not None:
            xmGuiGtk.addImgToBtn(widget, self.get(name + 'Label'), imgName, bitmapDict)
            xmGuiGtk.resetColor(colorWidget)
            self.textureCallback(name, imgName not in NOTSET_BITMAP)
            if isEdge:
                scale = float(getValue(EDGETEXTURES, imgName, 'scale', self.defScale))
                self.get(f'{prefix}_scale').set_value(scale)
                depth = float(getValue(EDGETEXTURES, imgName, 'depth', self.defDepth))
                self.get(f'{prefix}_depth').set_value(depth)

    def boxCallback(self, boxName, box_id=""):
        if isinstance(boxName, Gtk.CheckButton):  # Check if the passed argument is a widget
            boxName = box_id        # If it's a widget, get its name
         
        box = self.get(boxName)
        
        if box is None:
            return
        
        # Example: if you're working with a GtkGrid and want to retrieve a button
        # Assuming `boxName` is referring to the 'textureGrid' widget
        if isinstance(box, Gtk.Grid):
            texture_button = box.get_child_at(0, 0)  # Example: get widget at grid position (0, 0)
            if texture_button:
                logging.info(f"Found widget at (0, 0): {texture_button.get_name()}")
            
            # Retrieve other widgets in the grid if necessary
            color_button = box.get_child_at(0, 1)  # Position (0, 1)
            if color_button:
                logging.info(f"Found color button: {color_button.get_name()}")

        # If it is a GtkBox, loop through the children or handle accordingly
        if isinstance(box, Gtk.Box):
            for child in box.get_children():
                if isinstance(child, Gtk.Button):
                    logging.info(f"Button found: {child.get_label()}")
                elif isinstance(child, Gtk.Label):
                    logging.info(f"Label found: {child.get_text()}")


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

        if show:
            if color == "color":
                self.get(color + "_box").show()
            else:
                self.get(color).show()
                self.get(color + 'Label').show()
            for box in boxes:
                self.get(box).show()
                self.get(box[len('_'):-len('_box')]).show()
                self.boxCallback(self.get(box), box)
        else:
            if self.get(color) is None:
            if color == "color":
                self.get(color + "_box").hide()
            else:
                self.get(color).hide()
                self.get(color + 'Label').hide()
            for box in boxes:
                self.get(box).hide()
                self.get(box[len('_'):-len('_box')]).hide()

def run():
    e = ChangeBlockTexture()
    e.affect()
    return e

if __name__ == "__main__":
    run()
