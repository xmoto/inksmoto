from xmotoExtensionTkinter import XmotoExtensionTkinter
import logging, log
import Tkinter

class AddOtherLevelInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)

    def updateLabelData(self):
        for name, value in self.replacement.iteritems():
            self.label['remplacement'][name] = value.get(Tkinter.ACTIVE)

        self.label['level']['music'] = self.music.get(Tkinter.ACTIVE)

    def effect(self):
        self.getMetaData()
        if 'level' not in self.label:
            self.label['level'] = {}
        if 'remplacement' not in self.label:
            self.label['remplacement'] = {}

        self.defineWindowHeader('Other level properties')

        from listAvailableElements import sprites, musics
        self.replacement = {}
        for name in ['Strawberry', 'Wrecker', 'Flower', 'Star']:
            self.replacement[name] = self.defineListbox(self.frame, self.getValue('remplacement', name), label='%s replacement' % name, items=['None']+self.alphabeticSortOfKeys(sprites))
        self.music = self.defineListbox(self.frame, self.getValue('level', 'music'), label='Level music', items=['None']+self.alphabeticSortOfKeys(musics))

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

e = AddOtherLevelInfos()
e.affect()
