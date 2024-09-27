#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from inksmoto import log
import logging
from inksmoto.xmExtGtk import XmExtGtkLevel, WidgetInfos
from inksmoto.xmotoTools import createIfAbsent, getValue
from inksmoto import log
from inksmoto.inkex import addNS, NSS
from inksmoto import xmGuiGtk
from gi.repository import Gtk


def isBoxChecked(box):
    return 'true' if box.get_active() else 'false'


class AddLayerInfos(XmExtGtkLevel):
    def __init__(self):
        super().__init__()
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

        layers = self.layers[:]
        widgetsInfos = {}

        layersTable = self.get('layersTable')
        layersTable.resize(len(layers) + 1, 6)

        row = 1
        while len(layers) > 0:
            (layerId, layerLabel, layerIndex, dummy) = layers.pop(0)

            prefix = 'layer_%d_' % layerIndex

            widgetsInfos[prefix + 'isused'] = WidgetInfos('layer',
                                                          prefix + 'isused',
                                                          dontDel=True)
            widgetsInfos[prefix + 'ismain'] = WidgetInfos('layer',
                                                          prefix + 'ismain')
            widgetsInfos[prefix + 'x'] = WidgetInfos('layer', prefix + 'x', 1)
            widgetsInfos[prefix + 'y'] = WidgetInfos('layer', prefix + 'y', 1)

            layersTable.attach(Gtk.Label(label=layerId + '(%d)' % layerIndex),
                               0, 1, row, row + 1)

            layersTable.attach(Gtk.Label(label=layerLabel),
                               1, 2, row, row + 1)

            def addCheck(prefix, key):
                check = Gtk.CheckButton()
                check.set_name(prefix + key)
                isUsed = (getValue(self.label, 'layer', prefix + key) == 'true')
                check.set_active(isUsed)
                self.addWidget(prefix + key, check)
                return check

            check = addCheck(prefix, 'isused')
            layersTable.attach(check, 2, 3, row, row + 1)

            check = addCheck(prefix, 'ismain')
            layersTable.attach(check, 3, 4, row, row + 1)

            def addScale(prefix, key):
                scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
                scale.set_name(prefix + key)
                scale.set_increments(0.01, 0.01)
                scale.set_range(0, 2)
                scale.set_digits(2)
                value = getValue(self.label, 'layer', prefix + key, 1.0)
                scale.set_value(float(value))
                self.addWidget(prefix + key, scale)
                return scale

            scale = addScale(prefix, 'x')
            layersTable.attach(scale, 4, 5, row, row + 1)

            scale = addScale(prefix, 'y')
            layersTable.attach(scale, 5, 6, row, row + 1)

            row += 1

        layersTable.show_all()

        return widgetsInfos

    def updateLabelData(self):
        layers = self.label['layer']

        numberMainLayers = 0
        firstMain, between, secondMain = (False, False, False)

        for (layerId, layerLabel, layerIndex, dummy) in self.layers:
            prefix = 'layer_%d_' % layerIndex

            if getValue(layers, prefix + 'ismain') == 'true':
                numberMainLayers += 1
                if firstMain is False:
                    firstMain = True
                elif secondMain is False:
                    secondMain = True

            if (firstMain is True and
                secondMain is False and
                getValue(layers, prefix + 'ismain') == 'false' and
                getValue(layers, prefix + 'isused') == 'true'):
                between = True

        if numberMainLayers > 2:
            msg = "Warning: There's more than two main layers."
            log.outMsg(msg)
        if between is True and secondMain is True:
            msg = "Warning: The two main layers have to be consecutive.\n(no background or foreground layers between them)."
            log.outMsg(msg)


def run():
    ext = AddLayerInfos()
    ext.affect()
    return ext


if __name__ == "__main__":
    run()
