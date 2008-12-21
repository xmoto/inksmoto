from xmotoExtensionTkinter import XmotoExtTkLevel, XmotoListbox, XmotoBitmap, XmotoScale
from xmotoTools import getValue, createIfAbsent, alphabeticSortOfKeys
import logging, log
import Tkinter
from listAvailableElements import sprites, musics

class AddOtherLevelInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)
        self.defaultScale = 1

    def updateLabelData(self):
        for name, value in self.replacement.iteritems():
            self.label['remplacement'][name] = value.get()

        self.label['level']['music'] = self.music.get()

    def createWindow(self):
        createIfAbsent(self.label, 'level')
        createIfAbsent(self.label, 'remplacement')

        self.defineWindowHeader('Other level properties')

        self.replacement = {}
        for name, useScale in [('Strawberry', True), ('Wrecker', True), ('Flower', True), ('Star', False)]:
            self.defineLabel(self.frame, name + ':')
            sprite = getValue(self.label, 'remplacement', name, default=name)
            self.replacement[name] = XmotoBitmap(self.frame, sprites[sprite]['file'], sprite, self.spriteSelectionWindow, buttonName=name)
            if useScale == True:
                scale = getValue(self.label, 'remplacement', name+'Scale', default=self.defaultScale)
                self.replacement[name+'Scale'] = XmotoScale(self.frame, scale, label=name+' scale:', from_=0.1, to=10, resolution=0.1, default=self.defaultScale)

            
        self.music = XmotoListbox(self.frame, getValue(self.label, 'level', 'music'), label='Level music', items=['None']+alphabeticSortOfKeys(musics))

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.replacement[buttonName].update(imgName, sprites)


e = AddOtherLevelInfos()
e.affect()
