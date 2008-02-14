from xmotoExtensionTkinter import XmotoExtensionTkinter
import logging, log
import Tkinter

class AddLevelInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)

    def updateLabelData(self):
        self.label['level']['smooth']  = self.smooth.get()
        self.label['level']['lua']     = self.lua.get()
        self.label['level']['id']      = self.id.get()
        self.label['level']['name']    = self.name.get()
        self.label['level']['author']  = self.author.get()
        self.label['level']['desc']    = self.desc.get()
        self.label['level']['tex']     = self.tex.get(Tkinter.ACTIVE)

    def effect(self):
        self.getMetaData()
        if 'level' not in self.label:
            self.label['level'] = {}

        self.defineWindowHeader('Level properties')

        self.smooth  = self.defineScale(self.frame, self.getValue('level', 'smooth'), label='smoothitude', from_=1, to=10, resolution=1, default=9)
        self.lua     = self.defineFileSelectDialog(self.frame, self.getValue('level', 'lua'), label='lua script')
        self.id      = self.defineEntry(self.frame, self.getValue('level', 'id'),     label='level id')
        self.name    = self.defineEntry(self.frame, self.getValue('level', 'name'),   label='level name')
        self.author  = self.defineEntry(self.frame, self.getValue('level', 'author'), label='author')
        self.desc    = self.defineEntry(self.frame, self.getValue('level', 'desc'),   label='description')

        from listAvailableElements import textures
        self.tex = self.defineListbox(self.frame, self.getValue('level', 'tex'), label='border texture', items=self.alphabeticSortOfKeys(textures))

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

    def fileSelectHook(self, filename):
        self.lua.insert(Tkinter.INSERT, filename)

e = AddLevelInfos()
e.affect()
