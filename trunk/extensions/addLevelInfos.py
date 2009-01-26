from xmotoExtensionTkinter import XmotoExtTkLevel, XmScale
from xmotoExtensionTkinter import XmEntry, XmBitmap, XmLabel
from xmotoTools import createIfAbsent, checkId
import Tkinter
from listAvailableElements import textures

class AddLevelInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)

    def updateLabelData(self):
        if checkId(self.id.get()) == False:
            msg = "The level id can only contains alphanumeric characters and _"
            raise Exception(msg)

        self.label['level']['smooth'] = self.smooth.get()
        self.label['level']['lua']    = self.lua.get()
        self.label['level']['id']     = self.id.get()
        self.label['level']['name']   = self.name.get()
        self.label['level']['author'] = self.author.get()
        self.label['level']['desc']   = self.desc.get()
        self.label['level']['tex']    = self.tex.get()

    def createWindow(self):
        createIfAbsent(self.label, 'level')

        self.defineWindowHeader('Level properties')

        self.smooth = XmScale(self.frame,
                              self.getValue(self.label, 'level', 'smooth'),
                              label='smoothitude :',
                              from_=1, to=10, resolution=1, default=9)
        self.lua = self.defineFileSelectDialog(self.frame,
                                               self.getValue(self.label,
                                                             'level',
                                                             'lua'),
                                               label='lua script :')
        self.id = XmEntry(self.frame,
                          self.getValue(self.label, 'level', 'id'),
                          label='level id :')
        self.name = XmEntry(self.frame,
                            self.getValue(self.label, 'level', 'name'),
                            label='level name :')
        self.author = XmEntry(self.frame,
                              self.getValue(self.label, 'level', 'author'),
                              label='author :')
        self.desc = XmEntry(self.frame,
                            self.getValue(self.label, 'level', 'desc'),
                            label='description :')

        defaultTexture = self.getValue(self.label, 'level',
                                       'tex', default='_None_')
        XmLabel(self.frame, 'border texture :')
        self.tex = XmBitmap(self.frame,
                            textures[defaultTexture]['file'],
                            defaultTexture,
                            self.textureSelectionWindow,
                            buttonName='border texture')

    def fileSelectHook(self, filename):
        self.lua.delete(0, Tkinter.END)
        self.lua.insert(Tkinter.INSERT, filename)

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.tex.update(imgName, textures)

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
