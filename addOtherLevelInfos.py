from xmotoExtensionTkinter import XmotoExtensionTkinter
import logging, log
import Tkinter
import xml.dom.Element
import xml.dom.Text
from inkex   import NSS

class AddOtherLevelInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)

    def updateLabelData(self):
        self.label['level']['strawberry_replac']  = self.strawberry_replac.get(Tkinter.ACTIVE)
        self.label['level']['wrecker_replac']     = self.wrecker_replac.get(Tkinter.ACTIVE)
        self.label['level']['flower_replac']      = self.flower_replac.get(Tkinter.ACTIVE)
        self.label['level']['star_replac']        = self.star_replac.get(Tkinter.ACTIVE)
        self.label['level']['music']              = self.music.get(Tkinter.ACTIVE)

    def effect(self):
        self.getMetaData()
        if not self.label.has_key('level'):
            self.label['level'] = {}

        root = Tkinter.Tk()
        root.title('Other level properties')
        self.frame = Tkinter.Frame(root)
        self.frame.pack()

        from listAvailableElements import sprites, musics

        self.strawberry_replac = self.defineListbox('level', name='strawberry_replac', label='strawberry remplacement', items=['None']+sprites)
        self.wrecker_replac    = self.defineListbox('level', name='wrecker_replac',    label='wrecker remplacement',    items=['None']+sprites)
        self.flower_replac     = self.defineListbox('level', name='flower_replac',     label='flower remplacement',     items=['None']+sprites)
        self.star_replac       = self.defineListbox('level', name='star_replac',       label='star remplacement',       items=['None']+sprites)

        self.music             = self.defineListbox('level', name='music', label='Level music', items=['None']+musics)

        self.defineOkCancelButtons()
        root.mainloop()

e = AddOtherLevelInfos()
e.affect()
