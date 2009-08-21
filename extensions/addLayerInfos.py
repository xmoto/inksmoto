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
        self.oldLayersIdToIndex = {}
        self.layersIdToIndexToSave = []

    def updateLabelData(self):
        # remove infos from deleted layers
        layers = self.label['layer']

        numberMainLayers = 0
        firstMain, between, secondMain = (False, False, False)

        for (layerId, layerLabel, layerIndex, dummy) in self.layers:
            prefix = 'layer_%d_' % layerIndex

            layers[prefix+'id'] = layerId
            layers[prefix+'isused'] = isBoxChecked(self.get(prefix + 'isused'))
            layers[prefix+'ismain'] = isBoxChecked(self.get(prefix + 'ismain'))
            layers[prefix+'x'] = self.get(prefix + 'x').get()
            layers[prefix+'y'] = self.get(prefix + 'y').get()

            if layers[prefix+'ismain'] == 'true':
                numberMainLayers += 1

                if firstMain is False:
                    firstMain = True
                elif secondMain is False:
                    secondMain = True

            if (firstMain == True
                and secondMain == False
                and layers[prefix+'ismain'] == 'false'
                and layers[prefix+'isused'] == 'true'):
                between = True

        # if there's more than two main layer, raise a warning
        if numberMainLayers > 2:
            msg = "Warning: There's more than two main layers."
            log.outMsg(msg)
        if between is True and secondMain is True:
            msg = "Warning: The two main layers have to be consecutives.\n\
(no background or foreground layers between them)."
            log.outMsg(msg)

    def createWindow(self):
        createIfAbsent(self.label, 'layer')

        (self.label['layer'],
         self.layers) = self.svg.updateLayerInfos(self.label['layer'])

        f = Factory()
        xmGui.defineWindowHeader('Layer properties')

        # if a user set too many layers, it may not fit into the layer
        # window. -> have multiple columns

        # the frame containing the columns
        xmGui.newFrame()

        screenHeight = xmGui.getScreenHeight()
        # ugly approx (because the tk function to get a frame height
        # returns 1 ...)
        frameHeight = 50
        # create a copy
        layers = self.layers[:]

        while len(layers) > 0:
            curHeight = 0

            # the frame for the column
            xmGui.newFrame()

            xmGui.newFrame()
            f.createObject('XmLabel', 'Id', alone=False)
            f.createObject('XmLabel', 'Label', alone=False)
            f.createObject('XmLabel', 'Used', alone=False)
            f.createObject('XmLabel', 'Main', alone=False)
            f.createObject('XmLabel', 'X_scroll', alone=False)
            f.createObject('XmLabel', 'Y_scroll', alone=False)
            xmGui.popFrame()
            curHeight += frameHeight

            # display them like in inkscape, ie in reverse order from the svg
            while len(layers) > 0 and curHeight < screenHeight:
                (layerId, layerLabel, layerIndex, dummy) = layers.pop(0)

                xmGui.newFrame()

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
                curHeight += frameHeight

            # the frame for the column
            xmGui.popFrame(side='left')
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
