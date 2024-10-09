#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from gi.repository import Gtk
from inksmoto.xmExtGtk import XmExtGtkLevel, WidgetInfos
from inksmoto.xmotoTools import createIfAbsent, getValue
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk

TEXTURES = AvailableElements()['TEXTURES']

class AddSkyInfos(XmExtGtkLevel):
    def getWindowInfos(self):
        gladeFile = "addSkyInfos.glade"
        windowName = "addSkyInfos"
        return (gladeFile, windowName)

    def getSignals(self):
        self.paramsCallback(self.get('_use_params'))
        self.driftCallback(self.get('drifted'))

        return {
            'on_tex_clicked': (self.updateBitmap, "tex"),
            'on_driftTex_clicked': (self.updateBitmap, "driftTex"),
            'on__use_params_toggled': self.paramsCallback,
            'on_drifted_toggled': self.driftCallback
        }

    def updateLabelData(self):
        def removeUnusedDatas(dataKeys):
            for key in dataKeys:
                if key in self.label['sky']:
                    del self.label['sky'][key]

        if 'sky' not in self.label:
            return

        _use_params = self.get('_use_params')
        if not _use_params.get_active():
            removeUnusedDatas(['zoom', 'offset', 'color_r', 'color_g', 'color_b', 'color_a'])
            self.label['sky']['_use_params'] = 'false'

        drifted = self.get('drifted')
        if not drifted.get_active():
            removeUnusedDatas(['driftZoom', 'driftColor_r', 'driftColor_g', 'driftColor_b', 'driftColor_a', 'BlendTexture'])
            self.label['sky']['drifted'] = 'false'

    def getWidgetsInfos(self):
        return {
            'tex': WidgetInfos('sky', 'tex', '_None_'),
            '_use_params': WidgetInfos('sky', '_use_params', False),
            'zoom': WidgetInfos('sky', 'zoom', 2),
            'offset': WidgetInfos('sky', 'offset', 0.015),
            'color': WidgetInfos('sky', 'color', 255),
            'drifted': WidgetInfos('sky', 'drifted', False),
            'driftTex': WidgetInfos('sky', 'BlendTexture', '_None_'),
            'driftZoom': WidgetInfos('sky', 'driftZoom', 2),
            'driftColor': WidgetInfos('sky', 'driftColor', 255)
        }

    def updateBitmap(self, widget, widget_id):
        imgName = xmGuiGtk.BitmapSelectWindow('Texture Selection', TEXTURES).run()

        if imgName is not None:
            name = widget_id
            xmGuiGtk.addImgToBtn(widget, self.get(name + 'Label'), imgName, TEXTURES)

    def paramsCallback(self, box):
        widgets = ['zoom', 'offset', 'color']
        if box.get_active():
            for widget in widgets:
                self.get(widget).show()
                self.get(widget + 'Label').show()
        else:
            for widget in widgets:
                self.get(widget).hide()
                self.get(widget + 'Label').hide()

    def driftCallback(self, box):
        widgets = ['driftZoom', 'driftColor', 'driftTex']
        if box.get_active():
            for widget in widgets:
                self.get(widget).show()
                self.get(widget + 'Label').show()
        else:
            for widget in widgets:
                self.get(widget).hide()
                self.get(widget + 'Label').hide()

def run():
    ext = AddSkyInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
