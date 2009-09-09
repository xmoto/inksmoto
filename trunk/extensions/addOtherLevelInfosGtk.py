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

from inksmoto.xmExtGtk import XmExtGtkLevel
from inksmoto.xmotoTools import createIfAbsent, alphabeticSortOfKeys, getValue
from inksmoto.inkex import NSS
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk
from inksmoto.factory import Factory
SPRITES = AvailableElements()['SPRITES']
MUSICS = AvailableElements()['MUSICS']

class AddOtherLevelInfos(XmExtGtkLevel):
    def __init__(self):
        XmExtGtkLevel.__init__(self)
        self.defaultScale = 1

    def getWindowInfos(self):
        gladeFile = "addOtherLevelInfos.glade"
        windowName = "addOtherLevelInfos"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {'Strawberry': ('remplacement', 'Strawberry',
                               'Strawberry', None),
                'StrawberryScale': ('remplacement', 'StrawberryScale',
                                    self.defaultScale, None),
                'Wrecker': ('remplacement', 'Wrecker', 'Wrecker', None),
                'WreckerScale': ('remplacement', 'WreckerScale',
                                 self.defaultScale, None),
                'Flower': ('remplacement', 'Flower', 'Flower', None),
                'FlowerScale': ('remplacement', 'FlowerScale',
                                self.defaultScale, None),
                'Star': ('remplacement', 'Star', '_None_', None),
                'music': ('level', 'music', None, None)}

    def getSignals(self):
        return {'on_Strawberry_clicked': self.updateBitmap,
                'on_Wrecker_clicked': self.updateBitmap,
                'on_Flower_clicked': self.updateBitmap,
                'on_Star_clicked': self.updateBitmap}

    def afterHook(self):
        # update all the strawberries, wrecker and flower in the svg
        # with their new collision radius
        for typeid in ['Strawberry', 'Wrecker', 'EndOfLevel']:
            search = '//*[contains(@xmoto:xmoto_label, "typeid=%s")]' % typeid
            nodes = self.document.xpath(search, namespaces=NSS)
            for node in nodes:
                self.handlePath(node)

#    def createWindow(self):
#        xmGui.defineWindowHeader('Other level properties')
#        scale = ('XmScale',
#                 "self.replacement['%sScale']" % name,
#                 value, label=name+' scale:',
#                 from_=0.1, to=10, resolution=0.1,
#                 default=self.defaultScale)
#        music = ('XmListbox', 'self.music',
#                 value, label='Level music',
#                 items=['None']+alphabeticSortOfKeys(AvailableElements()['MUSICS']))
        
    def updateBitmap(self, widget):
        imgName = xmGuiGtk.bitmapSelectWindow('Sprite Selection',
                                              SPRITES).run()

        if imgName is not None:
            name = widget.get_name()
            label = self.get(name+'Label')
            xmGuiGtk.addImgToBtn(widget, label, imgName, SPRITES)

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddOtherLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
