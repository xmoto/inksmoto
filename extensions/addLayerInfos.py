from xmotoExtensionTkinter import XmotoExtTkLevel, XmotoScale, XmotoCheckBox
from xmotoTools import createIfAbsent
import log
import Tkinter
from inkex import addNS, NSS

class AddLayerInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)
        self.nblayers = 0
        self.layersInfos = []
        self.maxLayerIndex = -1
        self.layersIdToIndex = {}
        self.layersIdToIndexToSave = []

    def getExistingLayersIndex(self):
        def extractIndexFromKey(key):
            return int(key[len('layer_'):-len('_id')])

        for (key, layerId) in self.label['layer'].iteritems():
            if key[-3:] != '_id':
                continue
            layerIndex = extractIndexFromKey(key)
            if layerIndex > self.maxLayerIndex:
                self.maxLayerIndex = layerIndex
            self.layersIdToIndex[layerId] = layerIndex

    def getSvgLayersInfos(self):
        self.getExistingLayersIndex()

        layers = self.document.xpath('/svg:svg/svg:g', namespaces=NSS)

        self.nblayers = len(layers)
        for layer in layers:
            layerId    = layer.get('id')
            layerLabel = layer.get(addNS('label', 'inkscape'), '')
            self.layersInfos.append((layerId, layerLabel))

    def updateLabelData(self):
        # remove infos from deleted layers
        layers = {}
        numberMainLayers = 0
        for (layerId, layer, layerIndex) in self.layersIdToIndexToSave:
            prefix = 'layer_%d_' % layer
            prefixOld = 'layer_%d_' % layerIndex
            layers[prefix+'id']     = layerId
            box = self.get(prefixOld+'isused')
            layers[prefix+'isused'] = self.isBoxChecked(box)
            box = self.get(prefixOld+'ismain')
            layers[prefix+'ismain'] = self.isBoxChecked(box)
            layers[prefix+'x']      = self.get(prefixOld + 'x').get()
            layers[prefix+'y']      = self.get(prefixOld + 'y').get()
            if layers[prefix+'ismain'] == 'true':
                numberMainLayers += 1
        self.label['layer'] = layers

        # if there's more than two main layer, raise a warning
        if numberMainLayers > 2:
            msg = "Warning: There's more than two main layers."
            log.writeMessageToUser(msg)

    def createWindow(self):
        createIfAbsent(self.label, 'layer')

        self.getSvgLayersInfos()

        self.defineWindowHeader('Layer properties')

        titleFrame = Tkinter.Frame(self.frame)
        self.defineLabel(titleFrame, 'Layer_id',       alone=False)
        self.defineLabel(titleFrame, 'Layer_label',    alone=False)
        self.defineLabel(titleFrame, 'Use_layer',      alone=False)
        self.defineLabel(titleFrame, 'Is_main_layer',  alone=False)
        self.defineLabel(titleFrame, 'X_scroll',       alone=False)
        self.defineLabel(titleFrame, 'Y_scroll',       alone=False)
        titleFrame.pack()

        for layer in reversed(xrange(self.nblayers)):
            lineFrame = Tkinter.Frame(self.frame)
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

            # keep only layers who are still there. reorder them in
            # the metadata in the same order as in the svg
            self.layersIdToIndexToSave.append((layerId, layer, layerIndex))

            prefix = 'layer_%d_' % layerIndex

            label = self.defineLabel(lineFrame,
                                     layerId+"(%d)" % layerIndex,
                                     alone=False)
            self.set(prefix+'id', label)

            label = self.defineLabel(lineFrame, layerLabel, alone=False)
            self.set(prefix+'label', label)

            checkBox = XmotoCheckBox(lineFrame,
                                     self.getValue(self.label,
                                                   'layer',
                                                   prefix+'isused'),
                                     default=1, alone=False)
            self.set(prefix+'isused', checkBox)

            checkBox = XmotoCheckBox(lineFrame,
                                     self.getValue(self.label,
                                                   'layer',
                                                   prefix+'ismain'),
                                     alone=False)
            self.set(prefix+'ismain', checkBox)

            scale = XmotoScale(lineFrame,
                               self.getValue(self.label, 'layer', prefix+'x'),
                               alone=False, label=None,
                               from_=0, to=2, resolution=0.01, default=1)
            self.set(prefix+'x', scale)

            scale = XmotoScale(lineFrame,
                               self.getValue(self.label, 'layer', prefix+'y'),
                               alone=False, label=None,
                               from_=0, to=2, resolution=0.01, default=1)
            self.set(prefix+'y', scale)

            lineFrame.pack()

    def get(self, var):
        return self.__dict__[var]

    def set(self, var, value):
        self.__dict__[var] = value

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddLayerInfos()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
