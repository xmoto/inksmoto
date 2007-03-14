from xmotoExtensionTkinter import XmotoExtensionTkinter
import logging, log
import Tkinter
import xml.dom.Element
import xml.dom.Text
from inkex   import NSS

class AddLayerInfos(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)
        self.nblayers = 10

    def updateLabelData(self):
        for layer in xrange(self.nblayers):
            self.label['layer']['layer_%d_isused' % layer]  = self.isBoxChecked(self.get('layer_%d_isused'  % layer))
            self.label['layer']['layer_%d_x' % layer]       = self.get('layer_%d_x'       % layer).get()
            self.label['layer']['layer_%d_y' % layer]       = self.get('layer_%d_y'       % layer).get()
            self.label['layer']['layer_%d_isfront' % layer] = self.isBoxChecked(self.get('layer_%d_isfront' % layer))

    def effect(self):
        self.getMetaData()
        if not self.label.has_key('layer'):
            self.label['layer'] = {}

        root = Tkinter.Tk()
        root.title('Layer properties')
        self.frame = Tkinter.Frame(root)
        self.frame.pack()

        self.defineLabel('Use layer',      column=0, incRow=False)
        self.defineLabel('X scroll',       column=1, incRow=False)
        self.defineLabel('Y scroll',       column=2, incRow=False)
        self.defineLabel('Is front layer', column=3, incRow=True)
        for layer in xrange(self.nblayers):
            self.set('layer_%d_isused' % layer,  self.defineCheckbox('layer', name='layer_%d_isused' % layer, label=None, column=0, updateRow=False))
            self.set('layer_%d_x' % layer,       self.defineScale('layer',    name='layer_%d_x' % layer,      label=None, from_=0,  to=2, resolution=0.01, default=1, column=1, updateRow=False))
            self.set('layer_%d_y' % layer,       self.defineScale('layer',    name='layer_%d_y' % layer,      label=None, from_=0,  to=2, resolution=0.01, default=1, column=2, updateRow=False))
            self.set('layer_%d_isfront' % layer, self.defineCheckbox('layer', name='layer_%d_isused' % layer, label=None, column=3))

        self.defineOkCancelButtons()
        root.mainloop()

    def get(self, var):
        return self.__dict__[var]

    def set(self, var, value):
        self.__dict__[var] = value

e = AddLayerInfos()
e.affect()
