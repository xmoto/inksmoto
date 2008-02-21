from xmotoExtensionTkinter import XmotoExtensionTkinter, XmotoScale
from xmotoTools import createIfAbsent, getValue
import logging, log
import Tkinter
from lxml.etree import Element
from inkex import addNS, NSS

class AddLayerInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)

    def getExistingLayersIndex(self):
        def extractIndexFromKey(key):
            return int(key[len('layer_'):-len('_id')])

        self.maxLayerIndex = -1

        self.layersIdToIndex = {}
        for (key, layerId) in self.label['layer'].iteritems():
            if key[-3:] != '_id':
                continue
            layerIndex = extractIndexFromKey(key)
            if layerIndex > self.maxLayerIndex:
                self.maxLayerIndex = layerIndex
            self.layersIdToIndex[layerId] = layerIndex

    def getSvgLayersInfos(self):
        self.getExistingLayersIndex()
        layers = self.document.xpath('//svg:g', NSS)
        self.nblayers = len(layers)
        self.layersInfos = []
        for layer in layers:
            layerId    = layer.get('id')
            layerLabel = layer.get(addNS('label', 'inkscape'), '')
            self.layersInfos.append((layerId, layerLabel))

    def updateLabelData(self):
        # remove infos from deleted layers
        self.label['layer'] = {}
        numberMainLayers = 0
        for (layerId, layer, layerIndex) in self.layersIdToIndexToSave:
            preLayer = 'layer_%d_' % layer
            preLayerOld = 'layer_%d_' % layerIndex
            self.label['layer'][preLayer + 'id']      = layerId
            self.label['layer'][preLayer + 'isused']  = self.isBoxChecked(self.get(preLayerOld + 'isused'))
            self.label['layer'][preLayer + 'ismain']  = self.isBoxChecked(self.get(preLayerOld + 'ismain'))
            self.label['layer'][preLayer + 'x']       = self.get(preLayerOld + 'x').get()
            self.label['layer'][preLayer + 'y']       = self.get(preLayerOld + 'y').get()
            if self.label['layer'][preLayer + 'ismain'] == 'true':
                numberMainLayers += 1

        # if there's more than two main layer, raise a warning
        if numberMainLayers > 2:
            log.writeMessageToUser("Warning: There's more than two main layers.")

    def effect(self):
        self.getMetaData()
        createIfAbsent(self.label, 'layer')

        self.getSvgLayersInfos()

        self.defineWindowHeader('Layer properties')

        self.defineLabel(self.frame, 'Layer id',       alone=False)
        self.defineLabel(self.frame, 'Layer label',    alone=False)
        self.defineLabel(self.frame, 'Use layer',      alone=False)
        self.defineLabel(self.frame, 'Is main layer',  alone=False)
        self.defineLabel(self.frame, 'X scroll',       alone=False)
        self.defineLabel(self.frame, 'Y scroll',       alone=False)

        self.layersIdToIndexToSave = []
        for layer in reversed(xrange(self.nblayers)):
            # get layer index or create a new one if it's a new layer
            layerId    = self.layersInfos[layer][0]
            layerLabel = self.layersInfos[layer][1]
            if layerLabel == "":
                layerLabel = '#' + layerId
            if layerId in self.layersIdToIndex:
                layerIndex = self.layersIdToIndex[layerId]
            else:
                self.maxLayerIndex += 1
                layerIndex = self.maxLayerIndex
                self.layersIdToIndex[layerId] = layerIndex
            # keep only layers who are still there. reorder them in the metadata in the same order as in the svg
            self.layersIdToIndexToSave.append((layerId, layer, layerIndex))

            preLayer = 'layer_%d_' % layerIndex
            self.set(preLayer + 'id',      self.defineLabel(self.frame,    layerId+"(%d)" % layerIndex, alone=False))
            self.set(preLayer + 'label',   self.defineLabel(self.frame,    layerLabel,                  alone=False))
            self.set(preLayer + 'isused',  self.defineCheckbox(self.frame, getValue(self.label, 'layer', preLayer + 'isused'), label=None, default=1))
            self.set(preLayer + 'ismain',  self.defineCheckbox(self.frame, getValue(self.label, 'layer', preLayer + 'ismain'), label=None))
            self.set(preLayer + 'x',       XmotoScale(self.frame, getValue(self.label, 'layer', preLayer + 'x'), label=None, from_=0, to=2, resolution=0.01, default=1))
            self.set(preLayer + 'y',       XmotoScale(self.frame, getValue(self.label, 'layer', preLayer + 'y'), label=None, from_=0, to=2, resolution=0.01, default=1))

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

    def get(self, var):
        return self.__dict__[var]

    def set(self, var, value):
        self.__dict__[var] = value

e = AddLayerInfos()
e.affect()
