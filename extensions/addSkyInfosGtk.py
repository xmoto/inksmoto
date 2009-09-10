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

        return {'on_tex_clicked': self.updateBitmap,
                'on_driftTex_clicked': self.updateBitmap,
                'on__use_params_toggled': self.paramsCallback,
                'on_drifted_toggled': self.driftCallback}

    def updateLabelData(self):
        def removeUnusedDatas(dataKeys):
            for key in dataKeys:
                if key in self.label['sky']:
                    del self.label['sky'][key]

        if 'sky' not in self.label:
            return

        _use_params = self.get('_use_params')
        if _use_params.get_active() == False:
            removeUnusedDatas(['zoom', 'offset', 'color_r',
                               'color_g', 'color_b', 'color_a'])
            self.label['sky']['_use_params'] = 'false'

        drifted = self.get('drifted')
        if drifted.get_active() == False:
            removeUnusedDatas(['driftZoom', 'driftColor_r', 'driftColor_g',
                               'driftColor_b', 'driftColor_a', 'BlendTexture'])
            self.label['sky']['drifted'] = 'false'

    def getWidgetsInfos(self):
        return {'tex': WidgetInfos('sky', 'tex', '_None_'),
                '_use_params': WidgetInfos('sky', '_use_params', False),
                'zoom': WidgetInfos('sky', 'zoom', 2),
                'offset': WidgetInfos('sky', 'offset', 0.015),
                'color': WidgetInfos('sky', 'color', 255),
                'drifted': WidgetInfos('sky', 'drifted', False),
                'driftTex': WidgetInfos('sky', 'BlendTexture', '_None_'),
                'driftZoom': WidgetInfos('sky', 'driftZoom', 2),
                'driftColor': WidgetInfos('sky', 'driftColor', 255)}

    def updateBitmap(self, widget):
        imgName = xmGuiGtk.bitmapSelectWindow('Texture Selection',
                                              TEXTURES).run()

        if imgName is not None:
            name = widget.get_name()
            xmGuiGtk.addImgToBtn(widget, self.get(name+'Label'),
                                 imgName, TEXTURES)

    def paramsCallback(self, box):
        widgets = ['zoom', 'offset', 'color']
        if box.get_active() == True:
            for widget in widgets:
                self.get(widget).show()
                self.get(widget+'Label').show()
        else:
            for widget in widgets:
                self.get(widget).hide()
                self.get(widget+'Label').hide()

    def driftCallback(self, box):
        widgets = ['driftZoom', 'driftColor', 'driftTex']
        if box.get_active() == True:
            for widget in widgets:
                self.get(widget).show()
                self.get(widget+'Label').show()
        else:
            for widget in widgets:
                self.get(widget).hide()
                self.get(widget+'Label').hide()

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddSkyInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
