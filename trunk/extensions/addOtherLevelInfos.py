from xmotoExtensionTkinter import XmotoExtensionTkinter, XmotoListbox
from xmotoTools import getValue, createIfAbsent
import logging, log
import Tkinter

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

        from listAvailableElements import sprites, musics
        self.replacement = {}
        for name in ['Strawberry', 'Wrecker', 'Flower', 'Star']:
            self.replacement[name] = XmotoListbox(self.frame, getValue(self.label, 'remplacement', name), label='%s replacement' % name, items=['None']+self.alphabeticSortOfKeys(sprites))
        self.music = XmotoListbox(self.frame, getValue(self.label, 'level', 'music'), label='Level music', items=['None']+self.alphabeticSortOfKeys(musics))

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

e = AddOtherLevelInfos()
e.affect()
