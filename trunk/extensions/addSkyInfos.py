from xmotoExtensionTkinter import XmotoExtensionTkinter
import logging, log
import Tkinter

class AddSkyInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)

    def updateLabelData(self):
        def removeUnusedDatas(dataKeys):
            for key in dataKeys:
                if key in self.label['sky']:
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
        if not 'sky' in self.label:
            self.label['sky'] = {}

        self.defineWindowHeader('Sky properties')

        from listAvailableElements import textures
        self.tex          = self.defineListbox( self.frame, self.getValue('sky', 'tex'),          label='sky texture',       items=self.alphabeticSortOfKeys(textures))
        self.useParams    = self.defineCheckbox(self.frame, self.getValue('sky', 'use_params'),   label='Use parameters')
        self.zoom         = self.defineScale(   self.frame, self.getValue('sky', 'zoom'),         label='zoom',              from_=0.1,  to=10,  resolution=0.1,   default=2)
        self.offset       = self.defineScale(   self.frame, self.getValue('sky', 'offset'),       label='offset',            from_=0.01, to=1.0, resolution=0.005, default=0.015)
        self.color_r      = self.defineScale(   self.frame, self.getValue('sky', 'color_r'),      label='red color',         from_=0,    to=255, resolution=1,     default=255)
        self.color_g      = self.defineScale(   self.frame, self.getValue('sky', 'color_g'),      label='green color',       from_=0,    to=255, resolution=1,     default=255)
        self.color_b      = self.defineScale(   self.frame, self.getValue('sky', 'color_b'),      label='blue color',        from_=0,    to=255, resolution=1,     default=255)
        self.color_a      = self.defineScale(   self.frame, self.getValue('sky', 'color_a'),      label='alpha color',       from_=0,    to=255, resolution=1,     default=255)
        self.useDrift     = self.defineCheckbox(self.frame, self.getValue('sky', 'drifted'),      label='Drifted sky')
        self.driftZoom    = self.defineScale(   self.frame, self.getValue('sky', 'driftZoom'),    label='drift zoom',        from_=0.1,  to=5,   resolution=0.1,   default=2)
        self.driftColor_r = self.defineScale(   self.frame, self.getValue('sky', 'driftColor_r'), label='drift red color',   from_=0,    to=255, resolution=1,     default=255)
        self.driftColor_g = self.defineScale(   self.frame, self.getValue('sky', 'driftColor_g'), label='drift green color', from_=0,    to=255, resolution=1,     default=255)
        self.driftColor_b = self.defineScale(   self.frame, self.getValue('sky', 'driftColor_b'), label='drift blue color',  from_=0,    to=255, resolution=1,     default=255)
        self.driftColor_a = self.defineScale(   self.frame, self.getValue('sky', 'driftColor_a'), label='drift alpha color', from_=0,    to=255, resolution=1,     default=255)

        self.defineOkCancelButtons(self.frame, command=self.setMetaData)
        self.root.mainloop()

e = AddSkyInfos()
e.affect()
