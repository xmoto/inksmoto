from xmotoExtensionTkinter import XmotoExtensionTkinter
import logging, log
import Tkinter
import xml.dom.Element
import xml.dom.Text
from inkex   import NSS

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
        if not self.label.has_key('level'):
            self.label['level'] = {}

        root = Tkinter.Tk()
        root.title('Level properties')
        self.frame = Tkinter.Frame(root)
        self.frame.pack()

        self.smooth = self.defineScale('level', name='smooth', label='smoothitude', from_=1, to=10, resolution=1, default=9)

        self.lua     = self.defineEntry('level', name='lua',    label='lua script')
        self.id      = self.defineEntry('level', name='id',     label='level id')
        self.name    = self.defineEntry('level', name='name',   label='level name')
        self.author  = self.defineEntry('level', name='author', label='author')
        self.desc    = self.defineEntry('level', name='desc',   label='description')

        from listAvailableElements import textures
        self.tex = self.defineListbox('level', name='tex', label='border texture', items=textures)

        self.defineOkCancelButtons()
        root.mainloop()

e = AddLevelInfos()
e.affect()
