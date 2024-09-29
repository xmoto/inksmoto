#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

import os

from inksmoto.gui.bitmap_selection import BitmapSelection
from inksmoto.gui import bitmap
from inksmoto import log as _
import logging

from inksmoto.gui.gtk import Gtk
from inksmoto.xmExtGtk import XmExtGtkElement, WidgetInfos
from inksmoto.xmotoTools import alphabetic_sort, alphabeticSortOfKeys, get_bitmap_dir, getIfPresent, getValue
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk

from gi.repository.GdkPixbuf import Pixbuf

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

        self.selected_texture = bitmap.BITMAP_NONE

        self.bitmaps = bitmap.load_bitmap_list()

        # Skip the __biker__.png image used for PlayerStart
        self.bitmaps = {name: value for name, value in self.bitmaps.items() if not name.startswith("__")}

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
            self.textureCallback(tex, imgName not in bitmap.NOTSET_BITMAP)

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
        if self.get('textureLabel').get_text() in bitmap.NOTSET_BITMAP:
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
            if value in bitmap.NOTSET_BITMAP:
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
        # Retrieve the GtkBox or GtkGrid object from the Glade file

        logging.info(f"updateBitmap: {widget_id}")

        assert(self.window is not None) # TODO(Nikekson): Remove this
        bitmap_selection = BitmapSelection(self.bitmaps,
                title='Select a block texture',
                selected=self.selected_texture,
                parent=self.window)
        bitmap_selection.connect('item-selected', lambda _, imgName: self.on_item_selected(widget, widget_id, imgName))
        bitmap_selection.run()

    def on_item_selected(self, widget, widget_id, imgName):
        path = self.bitmaps[imgName]
        self.selected_texture = imgName

        isEdge = False
        prefix = None
        match widget_id:
            case 'texture':
                bitmapDict = TEXTURES
                colorWidget = self.get('color')
            case 'downEdge':
                bitmapDict = EDGETEXTURES
                colorWidget = self.get('d_color')
                (isEdge, prefix) = True, 'd'
            case 'upperEdge':
                bitmapDict = EDGETEXTURES
                colorWidget = self.get('u_color')
                (isEdge, prefix) = True, 'u'

        if widget_id is not None:
            xmGuiGtk.addImgToBtn(widget, self.get(widget_id + 'Label'), imgName, bitmapDict)
            xmGuiGtk.resetColor(colorWidget)
            self.textureCallback(widget_id, imgName not in bitmap.NOTSET_BITMAP)
            if isEdge:
                scale = float(getValue(EDGETEXTURES, imgName, 'scale', self.defScale))
                self.get(f'{prefix}_scale').set_value(scale)
                depth = float(getValue(EDGETEXTURES, imgName, 'depth', self.defDepth))
                self.get(f'{prefix}_depth').set_value(depth)

    def boxCallback(self, boxName, box_id=""):
        if isinstance(boxName, Gtk.CheckButton):  # Check if the passed argument is a widget
            boxName = box_id        # If it's a widget, get its name

        # Retrieve the GtkBox or GtkGrid object from the Glade file
        logging.info(boxName)
        box = self.get(boxName)

        if box is None:
            logging.error(f"Widget '{boxName}' not found in the Glade file.")
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
        logging.debug(f"texture: name={name}, show={show}")

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
                self.get(color + "_box").set_sensitive(True)
            else:
                self.get(color).set_sensitive(True)
                self.get(color + 'Label').set_sensitive(True)

            for box in boxes:
                self.get(box).set_sensitive(True)
                self.get(box[len('_'):-len('_box')]).set_sensitive(True)
                self.boxCallback(self.get(box), box)
        else:
            if self.get(color) is None:
                logging.error(f"ERROR: {color}, returned none!")

            if color == "color":
                self.get(color + "_box").set_sensitive(False)
            else:
                self.get(color).set_sensitive(False)
                self.get(color + 'Label').set_sensitive(False)

            for box in boxes:
                logging.info("Weird: " + box[len('_'):-len('_box')])
                self.get(box).set_sensitive(False)
                self.get(box[len('_'):-len('_box')]).set_sensitive(False)

def run():
    e = ChangeBlockTexture()
    e.affect()
    return e

if __name__ == "__main__":
    run()
