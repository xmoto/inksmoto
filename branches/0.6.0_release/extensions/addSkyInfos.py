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

from inksmoto.xmotoExtensionTkinter import XmExtTkLevel
from inksmoto.xmotoTools import createIfAbsent, getValue
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGui
from inksmoto.factory import Factory

class AddSkyInfos(XmExtTkLevel):
    def updateLabelData(self):
        def removeUnusedDatas(dataKeys):
            for key in dataKeys:
                if key in self.label['sky']:
                    del self.label['sky'][key]

        self.label['sky']['tex'] = self.tex.get()

        if self.useParams.get() == 1:
            self.label['sky']['_use_params'] = 'true'
            self.label['sky']['zoom']       = self.zoom.get()
            self.label['sky']['offset']     = self.offset.get()
            (r, g, b) = self.colorSky.get()
            self.label['sky']['color_r']    = r
            self.label['sky']['color_g']    = g
            self.label['sky']['color_b']    = b
            self.label['sky']['color_a']    = self.color_a.get()
        else:
            removeUnusedDatas(['zoom', 'offset', 'color_r',
                               'color_g', 'color_b', 'color_a'])
            self.label['sky']['_use_params'] = 'false'

        if self.useDrift.get() == 1:
            self.label['sky']['drifted']      = 'true'
            self.label['sky']['driftZoom']    = self.driftZoom.get()
            (r, g, b) = self.driftColorSky.get()
            self.label['sky']['driftColor_r'] = r
            self.label['sky']['driftColor_g'] = g
            self.label['sky']['driftColor_b'] = b
            self.label['sky']['driftColor_a'] = self.driftColor_a.get()
            self.label['sky']['BlendTexture'] = self.driftTex.get()
        else:
            removeUnusedDatas(['driftZoom', 'driftColor_r', 'driftColor_g',
                               'driftColor_b', 'driftColor_a', 'BlendTexture'])
            self.label['sky']['drifted'] = 'false'

    def createWindow(self):
        f = Factory()
        createIfAbsent(self.label, 'sky')

        xmGui.defineWindowHeader('Sky properties')
        bitmapSize = xmGui.getBitmapSizeDependingOnScreenResolution()

        xmGui.newFrame()
        xmGui.newFrame()

        f.createObject('XmTitle', "Sky texture")

        defaultTexture = getValue(self.label, 'sky',
                                  'tex', default='_None_')
        self.tex = f.createObject('XmBitmap', 'self.tex',
                                  AvailableElements()['TEXTURES'][defaultTexture]['file'],
                                  defaultTexture,
                                  toDisplay='textures',
                                  callback=self.updateBitmap,
                                  buttonName="texture", size=bitmapSize)

        f.createObject('XmTitle', "Parameters")

        value = getValue(self.label, 'sky', '_use_params')
        checkbox = f.createObject('XmCheckbox', 'self.useParams',
                                  value, text='Use parameters',
                                  command=self.paramsCallback)
        self.useParams  = checkbox

        self.zoom = f.createObject('XmScale', 'self.zoom',
                                   getValue(self.label, 'sky', 'zoom'),
                                   label='zoom:', from_=0.1,  to=10,
                                   resolution=0.1,default=2)

        self.offset = f.createObject('XmScale', 'self.offset',
                                     getValue(self.label, 'sky', 'offset'),
                                     label='offset:',
                                     from_=0.01, to=1.0,
                                     resolution=0.005, default=0.015)
        r = int(getValue(self.label, 'sky', 'color_r', default=255))
        g = int(getValue(self.label, 'sky', 'color_g', default=255))
        b = int(getValue(self.label, 'sky', 'color_b', default=255))
        self.colorSky = f.createObject('XmColor', 'self.colorSky', r, g, b,
                                       'Sky color', size=bitmapSize)
        value = getValue(self.label, 'sky', 'color_a')
        self.color_a = f.createObject('XmScale', 'self.color_a', value,
                                      label='alpha color:', from_=0, to=255,
                                      resolution=1, default=255)

        xmGui.popFrame('left')
        xmGui.newFrame()

        f.createObject('XmTitle', "Drift")

        checkbox = f.createObject('XmCheckbox', 'self.useDrift',
                                  getValue(self.label, 'sky', 'drifted'),
                                  text='Drifted sky:',
                                  command=self.driftCallback)
        self.useDrift = checkbox

        defaultTexture = getValue(self.label, 'sky',
                                  'BlendTexture', default='_None_')
        self.dritfLabel = f.createObject('XmLabel', "Drifted texture")
        self.driftTex = f.createObject('XmBitmap', 'self.driftTex',
                                       AvailableElements()['TEXTURES'][defaultTexture]['file'],
                                       defaultTexture,
                                       toDisplay='textures',
                                       callback=self.updateBitmap,
                                       buttonName="driftedTexture", size=bitmapSize)

        scale = f.createObject('XmScale', 'self.driftZoom',
                               getValue(self.label, 'sky', 'driftZoom'),
                               label='drift zoom:', from_=0.1, to=5,
                               resolution=0.1, default=2)
        self.driftZoom = scale
        r = int(getValue(self.label, 'sky', 'driftColor_r', default=255))
        g = int(getValue(self.label, 'sky', 'driftColor_g', default=255))
        b = int(getValue(self.label, 'sky', 'driftColor_b', default=255))
        self.driftColorSky = f.createObject('XmColor',
                                            'self.driftColorSky', r, g, b,
                                            'Drift sky color',
                                            size=bitmapSize)
        scale = f.createObject('XmScale', 'self.driftColor_a',
                               getValue(self.label, 'sky', 'driftColor_a'),
                               label='drift alpha color:',
                               from_=0, to=255, resolution=1, default=255)
        self.driftColor_a = scale

        xmGui.popFrame('right')
        xmGui.popFrame()

        self.paramsCallback()
        self.driftCallback()

    def updateBitmap(self, imgName, buttonName):
        if buttonName == 'texture':
            self.tex.update(imgName, AvailableElements()['TEXTURES'])
        elif buttonName == 'driftedTexture':
            self.driftTex.update(imgName, AvailableElements()['TEXTURES'])

    def paramsCallback(self):
        widgets = [self.zoom, self.offset, self.color_a, self.colorSky]
        if self.useParams.get() == 1:
            for widget in widgets:
                widget.show()
        else:
            for widget in widgets:
                widget.hide()

    def driftCallback(self):
        widgets = [self.driftZoom, self.driftColorSky,
                   self.driftColor_a, self.driftTex, self.dritfLabel]
        if self.useDrift.get() == 1:
            for widget in widgets:
                widget.show()
        else:
            for widget in widgets:
                widget.hide()

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddSkyInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()