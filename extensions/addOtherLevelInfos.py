from xmotoExtensionTkinter import XmotoExtensionTkinter, XmotoListbox, XmotoBitmap
from xmotoTools import getValue, createIfAbsent, alphabeticSortOfKeys
import logging, log
import Tkinter
from listAvailableElements import sprites, musics

class AddOtherLevelInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)

    def updateLabelData(self):
        for name, value in self.replacement.iteritems():
            self.label['remplacement'][name] = value.get()

        self.label['level']['music'] = self.music.get()

    def effect(self):
        self.getMetaData()
        createIfAbsent(self.label, 'level')
        createIfAbsent(self.label, 'remplacement')

        self.defineWindowHeader('Other level properties')

        self.replacement = {}
        for name in ['Strawberry', 'Wrecker', 'Flower', 'Star']:
            defaultSprite = getValue(self.label, 'remplacement', name, default=name)
            self.defineLabel(self.frame, name + ':')
            self.replacement[name] = XmotoBitmap(self.frame, sprites[defaultSprite], defaultSprite, self.spriteSelectionWindow, buttonName=name)
        self.music = XmotoListbox(self.frame, getValue(self.label, 'level', 'music'), label='Level music', items=['None']+alphabeticSortOfKeys(musics))

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        values = self.replacement[buttonName].update(imgName, sprites)


e = AddOtherLevelInfos()
e.affect()
