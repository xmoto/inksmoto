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
from inksmoto.xmotoTools import createIfAbsent, alphabeticSortOfKeys, getValue
from inksmoto.inkex import NSS
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGui
from inksmoto.factory import Factory

class AddOtherLevelInfos(XmExtTkLevel):
    def __init__(self):
        XmExtTkLevel.__init__(self)
        self.defaultScale = 1

    def afterHook(self):
        # update all the strawberries, wrecker and flower in the svg
        # with their new collision radius
        for typeid in ['Strawberry', 'Wrecker', 'EndOfLevel']:
            search = '//*[contains(@xmoto:xmoto_label, "typeid=%s")]' % typeid
            nodes = self.document.xpath(search, namespaces=NSS)
            for node in nodes:
                self.handlePath(node)

    def updateLabelData(self):
        for name, value in self.replacement.iteritems():
            self.label['remplacement'][name] = value.get()

        self.label['level']['music'] = self.music.get()

    def createWindow(self):
        createIfAbsent(self.label, 'level')
        createIfAbsent(self.label, 'remplacement')

        f = Factory()
        xmGui.defineWindowHeader('Other level properties')

        bitmapSize = xmGui.getBitmapSizeDependingOnScreenResolution()

        self.replacement = {}
        for name, useScale in [('Strawberry', True), ('Wrecker', True),
                               ('Flower', True), ('Star', False)]:
            f.createObject('XmLabel', name + ':')

            sprite = getValue(self.label, 'remplacement',
                              name, default=name)
            self.replacement[name] = f.createObject('XmBitmap',
                                                    "self.replacement['%s']" % name,
                                                    AvailableElements()['SPRITES'][sprite]['file'],
                                                    sprite,
                                                    toDisplay='sprites',
                                                    callback=self.updateBitmap,
                                                    buttonName=name,
                                                    size=bitmapSize)

            if useScale == True:
                value = getValue(self.label, 'remplacement',
                                 name+'Scale', default=self.defaultScale)
                scale = f.createObject('XmScale',
                                       "self.replacement['%sScale']" % name,
                                       value, label=name+' scale:',
                                       from_=0.1, to=10, resolution=0.1,
                                       default=self.defaultScale)
                self.replacement[name+'Scale'] = scale

        value = getValue(self.label, 'level', 'music')
        self.music = f.createObject('XmListbox', 'self.music',
                                    value, label='Level music',
                                    items=['None']+alphabeticSortOfKeys(AvailableElements()['MUSICS']))

    def updateBitmap(self, imgName, buttonName):
        self.replacement[buttonName].update(imgName, AvailableElements()['SPRITES'])

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddOtherLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
