#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from gi.repository import Gtk
from inksmoto.xmExtGtk import XmExtGtkLevel, WidgetInfos
from inksmoto.xmotoTools import createIfAbsent, alphabeticSortOfKeys, getValue
from inksmoto.inkex import NSS
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk

SPRITES = AvailableElements()['SPRITES']
MUSICS = AvailableElements()['MUSICS']

class AddOtherLevelInfos(XmExtGtkLevel):
    def __init__(self):
        super().__init__()
        self.defaultScale = 1

    def getWindowInfos(self):
        gladeFile = "addOtherLevelInfos.glade"
        windowName = "addOtherLevelInfos"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {
            'Strawberry': WidgetInfos('remplacement', 'Strawberry', 'Strawberry'),
            'StrawberryScale': WidgetInfos('remplacement', 'StrawberryScale', self.defaultScale),
            'Wrecker': WidgetInfos('remplacement', 'Wrecker', 'Wrecker'),
            'WreckerScale': WidgetInfos('remplacement', 'WreckerScale', self.defaultScale),
            'Flower': WidgetInfos('remplacement', 'Flower', 'Flower'),
            'FlowerScale': WidgetInfos('remplacement', 'FlowerScale', self.defaultScale),
            'Star': WidgetInfos('remplacement', 'Star', 'Star'),
            'music': WidgetInfos('level', 'music', 'None', None, ['None'] + alphabeticSortOfKeys(MUSICS))
        }

    def getSignals(self):
        return {
            'on_Strawberry_clicked': self.updateBitmap,
            'on_Wrecker_clicked': self.updateBitmap,
            'on_Flower_clicked': self.updateBitmap,
            'on_Star_clicked': self.updateBitmap
        }

    def afterHook(self):
        for typeid in ['Strawberry', 'Wrecker', 'EndOfLevel']:
            search = '//*[contains(@xmoto:xmoto_label, "typeid=%s")]' % typeid
            nodes = self.document.xpath(search, namespaces=NSS)
            for node in nodes:
                self.handlePath(node)

    def updateBitmap(self, widget):
        imgName = xmGuiGtk.bitmapSelectWindow('Sprite Selection', SPRITES).run()

        if imgName is not None:
            name = widget.get_name()
            label = self.get(name + 'Label')
            xmGuiGtk.addImgToBtn(widget, label, imgName, SPRITES)

def run():
    ext = AddOtherLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
