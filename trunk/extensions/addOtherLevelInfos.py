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
        if not self.label.has_key('level'):
            self.label['level'] = {}
        if not self.label.has_key('remplacement'):
            self.label['remplacement'] = {}

        root = Tkinter.Tk()
        root.title('Other level properties')
        self.frame = Tkinter.Frame(root)
        self.frame.pack()

        from listAvailableElements import sprites, musics

        self.replacement = {}
        for name in ['Strawberry', 'Wrecker', 'Flower', 'Star']:
            self.replacement[name] = self.defineListbox(self.getValue('remplacement', name), label='%s replacement' % name, items=['None']+sprites)

        self.music = self.defineListbox(self.getValue('level', 'music'), label='Level music', items=['None']+musics)

        self.defineOkCancelButtons()
        root.mainloop()

e = AddOtherLevelInfos()
e.affect()
