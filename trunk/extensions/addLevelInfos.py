from xmotoExtensionTkinter import XmotoExtTkLevel, XmotoScale, XmotoEntry, XmotoBitmap
from xmotoTools import getValue, createIfAbsent, alphabeticSortOfKeys, checkLevelId
import logging, log
import Tkinter
from listAvailableElements import textures

class AddLevelInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)

    def updateLabelData(self):
        if checkLevelId(self.id.get()) == False:
            raise Exception("The level id can only contains alphanumeric characters and _")

        self.label['level']['smooth'] = self.smooth.get()
        self.label['level']['lua']    = self.lua.get()
        self.label['level']['id']     = self.id.get()
        self.label['level']['name']   = self.name.get()
        self.label['level']['author'] = self.author.get()
        self.label['level']['desc']   = self.desc.get()
        self.label['level']['tex']    = self.tex.get()

    def effect(self):
        self.getMetaData()
        createIfAbsent(self.label, 'level')

        self.defineWindowHeader('Level properties')

        self.smooth  = XmotoScale(self.frame, getValue(self.label, 'level', 'smooth'), label='smoothitude :', from_=1, to=10, resolution=1, default=9)
        self.lua     = self.defineFileSelectDialog(self.frame, getValue(self.label, 'level', 'lua'), label='lua script :')
        self.id      = XmotoEntry(self.frame, getValue(self.label, 'level', 'id'),     label='level id :')
        self.name    = XmotoEntry(self.frame, getValue(self.label, 'level', 'name'),   label='level name :')
        self.author  = XmotoEntry(self.frame, getValue(self.label, 'level', 'author'), label='author :')
        self.desc    = XmotoEntry(self.frame, getValue(self.label, 'level', 'desc'),   label='description :')

        defaultTexture  = getValue(self.label, 'level', 'tex', default='_None_')
        self.defineLabel(self.frame, 'border texture :')
        self.tex = XmotoBitmap(self.frame, textures[defaultTexture]['file'], defaultTexture, self.textureSelectionWindow, buttonName='border texture')

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

    def fileSelectHook(self, filename):
        self.lua.delete(0, Tkinter.END)
        self.lua.insert(Tkinter.INSERT, filename)

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.tex.update(imgName, textures)

e = AddLevelInfos()
e.affect()
