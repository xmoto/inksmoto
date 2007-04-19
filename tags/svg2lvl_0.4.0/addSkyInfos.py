from xmotoExtensionTkinter import XmotoExtensionTkinter
import logging, log
import Tkinter
import xml.dom.Element
import xml.dom.Text
from inkex   import NSS

class AddSkyInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)

    def updateLabelData(self):
        def removeUnusedDatas(dataKeys):
            for key in dataKeys:
                if self.label['sky'].has_key(key):
                    del self.label['sky'][key]
            
        tex = self.tex.get(Tkinter.ACTIVE)
        self.label['sky']['tex'] = tex

        if self.useParams.get() == 1:
            self.label['sky']['use_params'] = 'true'
            self.label['sky']['zoom']       = self.zoom.get()
            self.label['sky']['offset']     = self.offset.get()
            self.label['sky']['color_r']    = self.color_r.get()
            self.label['sky']['color_g']    = self.color_g.get()
            self.label['sky']['color_b']    = self.color_b.get()
            self.label['sky']['color_a']    = self.color_a.get()
        else:
            removeUnusedDatas(['zoom', 'offset', 'color_r', 'color_g', 'color_b', 'color_a'])
            self.label['sky']['use_params'] = 'false'

        if self.useDrift.get() == 1:
            self.label['sky']['drifted']      = 'true'
            self.label['sky']['driftZoom']    = self.driftZoom.get()
            self.label['sky']['driftColor_r'] = self.driftColor_r.get()
            self.label['sky']['driftColor_g'] = self.driftColor_g.get()
            self.label['sky']['driftColor_b'] = self.driftColor_b.get()
            self.label['sky']['driftColor_a'] = self.driftColor_a.get()
        else:
            removeUnusedDatas(['driftZoom', 'driftColor_r', 'driftColor_g', 'driftColor_b', 'driftColor_a'])
            self.label['sky']['drifted'] = 'false'

    def effect(self):
        self.getMetaData()
        if not self.label.has_key('sky'):
            self.label['sky'] = {}

        root = Tkinter.Tk()
        root.title('Sky properties')
        self.frame = Tkinter.Frame(root)
        self.frame.pack()

        from listAvailableElements import textures
        self.tex = self.defineListbox('sky', name='tex', label='sky texture', items=textures)

        self.useParams = self.defineCheckbox('sky', name='use_params', label='Use parameters')

        self.zoom    = self.defineScale('sky', name='zoom',    label='zoom',        from_=0.1,  to=10,  resolution=0.1,   default=2)
        self.offset  = self.defineScale('sky', name='offset',  label='offset',      from_=0.01, to=1.0, resolution=0.005, default=0.015)
        self.color_r = self.defineScale('sky', name='color_r', label='red color',   from_=0,    to=255, resolution=1,     default=255)
        self.color_g = self.defineScale('sky', name='color_g', label='green color', from_=0,    to=255, resolution=1,     default=255)
        self.color_b = self.defineScale('sky', name='color_b', label='blue color',  from_=0,    to=255, resolution=1,     default=255)
        self.color_a = self.defineScale('sky', name='color_a', label='alpha color', from_=0,    to=255, resolution=1,     default=255)

        self.useDrift = self.defineCheckbox('sky', name='drifted', label='Drifted sky')

        self.driftZoom    = self.defineScale('sky', name='driftZoom',    label='drift zoom',        from_=0.1, to=5,   resolution=0.1, default=2)
        self.driftColor_r = self.defineScale('sky', name='driftColor_r', label='drift red color',   from_=0,   to=255, resolution=1,   default=255)
        self.driftColor_g = self.defineScale('sky', name='driftColor_g', label='drift green color', from_=0,   to=255, resolution=1,   default=255)
        self.driftColor_b = self.defineScale('sky', name='driftColor_b', label='drift blue color',  from_=0,   to=255, resolution=1,   default=255)
        self.driftColor_a = self.defineScale('sky', name='driftColor_a', label='drift alpha color', from_=0,   to=255, resolution=1,   default=255)

        self.defineOkCancelButtons()
        root.mainloop()

e = AddSkyInfos()
e.affect()
