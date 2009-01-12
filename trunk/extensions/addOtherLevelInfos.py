from xmotoExtensionTkinter import XmotoExtTkLevel, XmotoListbox, XmotoBitmap, XmotoScale
from xmotoTools import createIfAbsent, alphabeticSortOfKeys
from svgnode import setNodeAsCircle
from inksmoto_configuration import defaultCollisionRadius, svg2lvlRatio
from inkex import NSS, addNS
import logging, log
from listAvailableElements import sprites, musics

class AddOtherLevelInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)
        self.defaultScale = 1

    def afterHook(self):
        # update all the strawberries, wrecker and flower in the svg
        # with their new collision radius
        for typeid in ['Strawberry', 'Wrecker', 'EndOfLevel']:
            nodes = self.document.xpath('//*[contains(@xmoto:xmoto_label, "typeid=%s")]' % typeid, namespaces=NSS)
            for node in nodes:
                self.handlePath(node)

    def updateLabelData(self):
        for name, value in self.replacement.iteritems():
            self.label['remplacement'][name] = value.get()

        self.label['level']['music'] = self.music.get()

    def createWindow(self):
        createIfAbsent(self.label, 'level')
        createIfAbsent(self.label, 'remplacement')

        self.defineWindowHeader('Other level properties')

        bitmapSize = self.getBitmapSizeDependingOnScreenResolution()

        self.replacement = {}
        for name, useScale in [('Strawberry', True), ('Wrecker', True), ('Flower', True), ('Star', False)]:
            self.defineLabel(self.frame, name + ':')
            sprite = self.getValue(self.label, 'remplacement', name, default=name)
            self.replacement[name] = XmotoBitmap(self.frame, sprites[sprite]['file'], sprite, self.spriteSelectionWindow, buttonName=name, size=bitmapSize)
            if useScale == True:
                scale = self.getValue(self.label, 'remplacement', name+'Scale', default=self.defaultScale)
                self.replacement[name+'Scale'] = XmotoScale(self.frame, scale, label=name+' scale:', from_=0.1, to=10, resolution=0.1, default=self.defaultScale)

        self.music = XmotoListbox(self.frame, self.getValue(self.label, 'level', 'music'), label='Level music', items=['None']+alphabeticSortOfKeys(musics))

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.replacement[buttonName].update(imgName, sprites)

if __name__ == '__main__':
    e = AddOtherLevelInfos()
    e.affect()
