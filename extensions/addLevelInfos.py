from xmotoExtensionTkinter import XmotoExtensionTkinter
from xmotoTools import getValue
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

        (self.smooth, dummy)  = self.defineScale(self.frame, getValue(self.label, 'level', 'smooth'), label='smoothitude', from_=1, to=10, resolution=1, default=9)
        self.lua              = self.defineFileSelectDialog(self.frame, getValue(self.label, 'level', 'lua'), label='lua script')
        (self.id,     dummy)  = self.defineEntry(self.frame, getValue(self.label, 'level', 'id'),     label='level id')
        (self.name,   dummy)  = self.defineEntry(self.frame, getValue(self.label, 'level', 'name'),   label='level name')
        (self.author, dummy)  = self.defineEntry(self.frame, getValue(self.label, 'level', 'author'), label='author')
        (self.desc,   dummy)  = self.defineEntry(self.frame, getValue(self.label, 'level', 'desc'),   label='description')

        from listAvailableElements import textures
        self.tex = self.defineListbox(self.frame, getValue(self.label, 'level', 'tex'), label='border texture', items=self.alphabeticSortOfKeys(textures))

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

    def fileSelectHook(self, filename):
        self.lua.delete(0, Tkinter.END)
        self.lua.insert(Tkinter.INSERT, filename)

e = AddLevelInfos()
e.affect()
