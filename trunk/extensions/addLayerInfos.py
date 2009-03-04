from inksmoto.xmotoExtensionTkinter import XmExtTkLevel
from inksmoto.xmotoTools import createIfAbsent, getValue
from inksmoto import log
from inksmoto.inkex import addNS, NSS
from inksmoto import xmGui
from inksmoto.factory import Factory

def isBoxChecked(box):
    if box.get() == 1:
        return 'true'
    else:
        return 'false'

class AddLayerInfos(XmExtTkLevel):
    def __init__(self):
        XmExtTkLevel.__init__(self)
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
            layers[prefix+'isused'] = isBoxChecked(box)
            box = self.get(prefixOld+'ismain')
            layers[prefix+'ismain'] = isBoxChecked(box)
            layers[prefix+'x']      = self.get(prefixOld + 'x').get()
            layers[prefix+'y']      = self.get(prefixOld + 'y').get()
            if layers[prefix+'ismain'] == 'true':
                numberMainLayers += 1
        self.label['layer'] = layers

        # if there's more than two main layer, raise a warning
        if numberMainLayers > 2:
            msg = "Warning: There's more than two main layers."
            log.outMsg(msg)

    def createWindow(self):
        createIfAbsent(self.label, 'layer')

        self.getSvgLayersInfos()

        f = Factory()
        xmGui.defineWindowHeader('Layer properties')

        xmGui.newFrame()
        f.createObject('XmLabel', 'Id', alone=False)
        f.createObject('XmLabel', 'Label', alone=False)
        f.createObject('XmLabel', 'Used', alone=False)
        f.createObject('XmLabel', 'Main', alone=False)
        f.createObject('XmLabel', 'X_scroll', alone=False)
        f.createObject('XmLabel', 'Y_scroll', alone=False)
        xmGui.popFrame()

        for layer in reversed(xrange(self.nblayers)):
            xmGui.newFrame()
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
            label = f.createObject('XmLabel',
                                   layerId+"(%d)" % layerIndex, alone=False)
            self.set(prefix+'id', label)

            label = f.createObject('XmLabel', layerLabel, alone=False)
            self.set(prefix+'label', label)

            value = getValue(self.label, 'layer', prefix+'isused')
            checkBox = f.createObject('XmCheckbox', 'self.'+prefix+'isused',
                                      value, default=1, alone=False)
            self.set(prefix+'isused', checkBox)

            value = getValue(self.label, 'layer', prefix+'ismain')
            checkBox = f.createObject('XmCheckbox', 'self.'+prefix+'ismain',
                                      value, alone=False)
            self.set(prefix+'ismain', checkBox)

            value = getValue(self.label, 'layer', prefix+'x')
            scale = f.createObject('XmScale', 'self.'+prefix+'x',
                                   value, alone=False, label=None,
                                   from_=0, to=2, resolution=0.01, default=1)
            self.set(prefix+'x', scale)

            value = getValue(self.label, 'layer', prefix+'y')
            scale = f.createObject('XmScale', 'self.'+prefix+'y',
                                   value, alone=False, label=None,
                                   from_=0, to=2, resolution=0.01, default=1)
            self.set(prefix+'y', scale)

            xmGui.popFrame()

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
