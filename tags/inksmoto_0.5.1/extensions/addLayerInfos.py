from xmotoExtensionTkinter import XmotoExtTkLevel, XmotoScale, XmotoCheckBox
from xmotoTools import createIfAbsent, getValue, updateLayerInfos
import logging, log
import Tkinter
from lxml.etree import Element

class AddLayerInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)

    def updateLabelData(self):
        # remove infos from deleted layers
        numberMainLayers = 0
        for (layerId, layerLabe, layerIndex, dummy) in self.layers:
            preLayer = 'layer_%d_' % layerIndex

            self.label['layer'][preLayer + 'id']      = layerId
            self.label['layer'][preLayer + 'isused']  = self.isBoxChecked(self.get(preLayer + 'isused'))
            self.label['layer'][preLayer + 'ismain']  = self.isBoxChecked(self.get(preLayer + 'ismain'))
            self.label['layer'][preLayer + 'x']       = self.get(preLayer + 'x').get()
            self.label['layer'][preLayer + 'y']       = self.get(preLayer + 'y').get()

            if self.label['layer'][preLayer + 'ismain'] == 'true':
                numberMainLayers += 1

        # if there's more than two main layer, raise a warning
        if numberMainLayers > 2:
            log.writeMessageToUser("Warning: There's more than two main layers.")

    def createWindow(self):
        createIfAbsent(self.label, 'layer')

        (self.label['layer'], self.layers) = updateLayerInfos(self.document, self.label['layer'])

        self.defineWindowHeader('Layer properties')

        titleFrame = Tkinter.Frame(self.frame)
        self.defineLabel(titleFrame, 'Layer_id',       alone=False)
        self.defineLabel(titleFrame, 'Layer_label',    alone=False)
        self.defineLabel(titleFrame, 'Use_layer',      alone=False)
        self.defineLabel(titleFrame, 'Is_main_layer',  alone=False)
        self.defineLabel(titleFrame, 'X_scroll',       alone=False)
        self.defineLabel(titleFrame, 'Y_scroll',       alone=False)
        titleFrame.pack()

        for (layerId, layerLabel, layerIndex, dummy) in self.layers:
            lineFrame = Tkinter.Frame(self.frame)

            preLayer = 'layer_%d_' % layerIndex
            self.set(preLayer + 'id',      self.defineLabel(lineFrame,    layerId+"(%d)" % layerIndex, alone=False))
            self.set(preLayer + 'label',   self.defineLabel(lineFrame,    layerLabel,                  alone=False))
            self.set(preLayer + 'isused',  XmotoCheckBox(lineFrame, getValue(self.label, 'layer', preLayer + 'isused'), default=1, alone=False))
            self.set(preLayer + 'ismain',  XmotoCheckBox(lineFrame, getValue(self.label, 'layer', preLayer + 'ismain'), alone=False))
            self.set(preLayer + 'x',       XmotoScale(lineFrame, getValue(self.label, 'layer', preLayer + 'x'), alone=False, label=None, from_=0, to=2, resolution=0.01, default=1))
            self.set(preLayer + 'y',       XmotoScale(lineFrame, getValue(self.label, 'layer', preLayer + 'y'), alone=False, label=None, from_=0, to=2, resolution=0.01, default=1))
            lineFrame.pack()

    def get(self, var):
        return self.__dict__[var]

    def set(self, var, value):
        self.__dict__[var] = value

e = AddLayerInfos()
e.affect()
