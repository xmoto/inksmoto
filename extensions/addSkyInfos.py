from xmotoExtensionTkinter import XmotoExtTkLevel, XmotoBitmap, XmotoScale, XmotoCheckBox, XmotoColorButton
from xmotoTools import createIfAbsent, getValue, alphabeticSortOfKeys
import logging, log
import Tkinter
from listAvailableElements import textures

class AddSkyInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)

    def updateLabelData(self):
        def removeUnusedDatas(dataKeys):
            for key in dataKeys:
                if key in self.label['sky']:
                    del self.label['sky'][key]

        self.label['sky']['tex'] = self.tex.get()

        if self.useParams.get() == 1:
            self.label['sky']['use_params'] = 'true'
            self.label['sky']['zoom']       = self.zoom.get()
            self.label['sky']['offset']     = self.offset.get()
            (r, g, b) = self.colorSky.get()
            self.label['sky']['color_r']    = r
            self.label['sky']['color_g']    = g
            self.label['sky']['color_b']    = b
            self.label['sky']['color_a']    = self.color_a.get()
        else:
            removeUnusedDatas(['zoom', 'offset', 'color_r', 'color_g', 'color_b', 'color_a'])
            self.label['sky']['use_params'] = 'false'

        if self.useDrift.get() == 1:
            self.label['sky']['drifted']      = 'true'
            self.label['sky']['driftZoom']    = self.driftZoom.get()
            (r, g, b) = self.driftColorSky.get()
            self.label['sky']['driftColor_r'] = r
            self.label['sky']['driftColor_g'] = g
            self.label['sky']['driftColor_b'] = b
            self.label['sky']['driftColor_a'] = self.driftColor_a.get()
        else:
            removeUnusedDatas(['driftZoom', 'driftColor_r', 'driftColor_g', 'driftColor_b', 'driftColor_a'])
            self.label['sky']['drifted'] = 'false'

    def createWindow(self):
        createIfAbsent(self.label, 'sky')

        self.defineWindowHeader('Sky properties')

        bitmapSize = self.getBitmapSizeDependingOnScreenResolution()

        self.defineLabel(self.frame, "sky texture:")
        defaultTexture    = getValue(self.label, 'sky', 'tex', default='_None_')
        self.tex          = XmotoBitmap(self.frame, textures[defaultTexture]['file'], defaultTexture, self.textureSelectionWindow, buttonName="texture", size=bitmapSize)

        self.defineTitle(self.frame, "Parameters")
        self.useParams    = XmotoCheckBox(self.frame, getValue(self.label, 'sky', 'use_params'), text='Use parameters', command=self.paramsCallback)
        self.zoom         = XmotoScale(self.frame, getValue(self.label, 'sky', 'zoom'),         label='zoom:',              from_=0.1,  to=10,  resolution=0.1,   default=2)
        self.offset       = XmotoScale(self.frame, getValue(self.label, 'sky', 'offset'),       label='offset:',            from_=0.01, to=1.0, resolution=0.005, default=0.015)
        r = int(getValue(self.label, 'sky', 'color_r', default=255))
        g = int(getValue(self.label, 'sky', 'color_g', default=255))
        b = int(getValue(self.label, 'sky', 'color_b', default=255))
        self.colorSky = XmotoColorButton(self.frame, r, g, b, 'Sky color', size=bitmapSize)
        self.color_a      = XmotoScale(self.frame, getValue(self.label, 'sky', 'color_a'),      label='alpha color:',       from_=0,    to=255, resolution=1,     default=255)

        self.defineTitle(self.frame, "Drift")
        self.useDrift     = XmotoCheckBox(self.frame, getValue(self.label, 'sky', 'drifted'), text='Drifted sky:', command=self.driftCallback)
        self.driftZoom    = XmotoScale(self.frame, getValue(self.label, 'sky', 'driftZoom'),    label='drift zoom:',        from_=0.1,  to=5,   resolution=0.1,   default=2)
        r = int(getValue(self.label, 'sky', 'driftColor_r', default=255))
        g = int(getValue(self.label, 'sky', 'driftColor_g', default=255))
        b = int(getValue(self.label, 'sky', 'driftColor_b', default=255))
        self.driftColorSky = XmotoColorButton(self.frame, r, g, b, 'Drift sky color', size=bitmapSize)
        self.driftColor_a = XmotoScale(self.frame, getValue(self.label, 'sky', 'driftColor_a'), label='drift alpha color:', from_=0,    to=255, resolution=1,     default=255)

        self.paramsCallback()
        self.driftCallback()

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        values = self.tex.update(imgName, textures)

    def paramsCallback(self):
        widgets = [self.zoom, self.offset, self.color_a, self.colorSky]
        if self.useParams.get() == 1:
            for widget in widgets:
                widget.show()
        else:
            for widget in widgets:
                widget.hide()

    def driftCallback(self):
        widgets = [self.driftZoom, self.driftColorSky, self.driftColor_a]
        if self.useDrift.get() == 1:
            for widget in widgets:
                widget.show()
        else:
            for widget in widgets:
                widget.hide()

e = AddSkyInfos()
e.affect()
