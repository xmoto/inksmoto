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

from inksmoto import log
import logging
from inksmoto.xmExtGtk import XmExtGtkLevel, WidgetInfos
from inksmoto.xmotoTools import createIfAbsent, getValue
from inksmoto import log
from inksmoto.inkex import addNS, NSS
from inksmoto import xmGuiGtk
import gtk

def isBoxChecked(box):
    if box.get() == 1:
        return 'true'
    else:
        return 'false'

class AddLayerInfos(XmExtGtkLevel):
    def __init__(self):
        XmExtGtkLevel.__init__(self)
        self.nblayers = 0
        self.layersInfos = []
        self.maxLayerIndex = -1
        self.oldLayersIdToIndex = {}
        self.layersIdToIndexToSave = []

    def getWindowInfos(self):
        gladeFile = "addLayerInfos.glade"
        windowName = "addLayerInfos"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        createIfAbsent(self.label, 'layer')

        (self.label['layer'],
         self.layers) = self.svg.updateLayerInfos(self.label['layer'])

        # create the widgets
        layers = self.layers[:]
        widgetsInfos = {}

        layersTable = self.get('layersTable')
        layersTable.resize(len(layers)+1, 6)

        # display them like in inkscape, ie in reverse order from the svg
        row = 1
        while len(layers) > 0:
            (layerId, layerLabel, layerIndex, dummy) = layers.pop(0)

            prefix = 'layer_%d_' % layerIndex

            # add the layer in the widgets infos
            widgetsInfos[prefix+'isused'] = WidgetInfos('layer',
                                                        prefix+'isused',
                                                        dontDel=True)
            widgetsInfos[prefix+'ismain'] = WidgetInfos('layer',
                                                        prefix+'ismain')
            widgetsInfos[prefix+'x'] = WidgetInfos('layer', prefix+'x', 1)
            widgetsInfos[prefix+'y'] = WidgetInfos('layer', prefix+'y', 1)

            # create the widgets and add them to the table
            layersTable.attach(gtk.Label(layerId+'(%d)' % layerIndex),
                               0, 1, row, row+1)
                                
            layersTable.attach(gtk.Label(layerLabel),
                               1, 2, row, row+1)

            def addCheck(prefix, key):
                check = gtk.CheckButton()
                check.set_name(prefix+key)
                isUsed = (getValue(self.label, 'layer', prefix+key) == 'true')
                check.set_active(isUsed)
                self.addWidget(prefix+key, check)
                return check

            check = addCheck(prefix, 'isused')
            layersTable.attach(check, 2, 3, row, row+1)

            check = addCheck(prefix, 'ismain')
            layersTable.attach(check, 3, 4, row, row+1)

            def addScale(prefix, key):
                scale = gtk.HScale()
                scale.set_name(prefix+key)
                scale.set_increments(0.01, 0.01)
                scale.set_range(0, 2)
                value = getValue(self.label, 'layer', prefix+key, 1.0)
                scale.set_value(float(value))
                self.addWidget(prefix+key, scale)
                return scale

            scale = addScale(prefix, 'x')
            layersTable.attach(scale, 4, 5, row, row+1)

            scale = addScale(prefix, 'y')
            layersTable.attach(scale, 5, 6, row, row+1)

            row += 1

        layersTable.show_all()

        return widgetsInfos

    def updateLabelData(self):
        # remove infos from deleted layers
        layers = self.label['layer']

        numberMainLayers = 0
        firstMain, between, secondMain = (False, False, False)

        for (layerId, layerLabel, layerIndex, dummy) in self.layers:
            prefix = 'layer_%d_' % layerIndex

            if getValue(layers, prefix+'ismain') == 'true':
                numberMainLayers += 1

                if firstMain is False:
                    firstMain = True
                elif secondMain is False:
                    secondMain = True

            if (firstMain == True
                and secondMain == False
                and getValue(layers, prefix+'ismain') == 'false'
                and getValue(layers, prefix+'isused') == 'true'):
                between = True

        # if there's more than two main layer, raise a warning
        if numberMainLayers > 2:
            msg = "Warning: There's more than two main layers."
            log.outMsg(msg)
        if between is True and secondMain is True:
            msg = "Warning: The two main layers have to be consecutives.\n\
(no background or foreground layers between them)."
            log.outMsg(msg)

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddLayerInfos()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
