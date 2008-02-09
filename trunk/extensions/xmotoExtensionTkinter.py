from xmotoExtension import XmotoExtension
from inkex import addNS, NSS
from lxml import etree
from lxml.etree import Element
import Tkinter
import logging, log

class XmotoExtensionTkinter(XmotoExtension):
    """ use for extensions with their own window made with tkinter
    """
    def __init__(self):
        XmotoExtension.__init__(self)
        self.row = 1

    def getMetaData(self):
        self.labelValue  = ''
	self.description = None
        descriptions = self.document.xpath('//dc:description', NSS)
        if descriptions is not None and len(descriptions) > 0:
            self.description = descriptions[0]
	    self.labelValue = self.description.text

        self.parseLabel(self.labelValue)

    def setMetaData(self):
        self.updateLabelData()

        self.frame.quit()

        self.unparseLabel()

        if self.description is not None:
            self.description.text = self.labelValue
        else:
            self.createMetada()

    def createMetada(self):
        self.svg  = self.document.getroot()

        # create only dc:description or metadata/RDF/dc:description ?
        metadatas = self.document.xpath('//metadata')
        if metadatas is None or len(metadatas) == 0:
            metadata = Element('metadata')
            metadata.set('id', 'metadatasvg2lvl')
            self.svg.append(metadata)
        else:
            metadata = metadatas[0]

        rdfs = metadata.xpath('//rdf:RDF', NSS)
        if rdfs is None or len(rdfs) == 0:
            rdf = Element(addNS('RDF', 'rdf'))
            metadata.append(rdf)
        else:
            rdf = rdfs[0]

        works = rdf.xpath('//cc:Work', NSS)
        if works is None or len(works) == 0:            
            work = Element(addNS('Work', 'cc'))
            work.set(addNS('about', 'rdf'), '')
            rdf.append(work)
        else:
            work = works[0]

        formats = work.xpath('//dc:format', NSS)
        if formats is None or len(formats) == 0:
            format = Element(addNS('format', 'dc'))
	    format.text = 'image/svg+xml'
            work.append(format)

        types = work.xpath('//dc:type', NSS)
        if types is None or len(types) == 0:
            typeNode = Element(addNS('type', 'dc'))
            typeNode.set(addNS('resource', 'rdf'), 'http://purl.org/dc/dcmitype/StillImage')
            work.append(typeNode)


        description = Element(addNS('description', 'dc'))
	description.text = self.labelValue
        work.append(description)

    def getValue(self, namespace, name=None, dictValues=None, default=None):
        if dictValues is None:
            dictValues = self.label

        try:
            if name is not None:
                return dictValues[namespace][name]
            else:
                return dictValues[namespace]
        except:
            return default

    def defineOkCancelButtons(self, command=None):
        cancel_button = Tkinter.Button(self.frame, text="Cancel", command=self.frame.quit)
        cancel_button.grid(column=0, row=self.row)

        if command is None:
            command = self.setMetaData

        ok_button = Tkinter.Button(self.frame, text="OK", command=command)
        ok_button.grid(column=1, row=self.row)

    def defineTitle(self, label, column=0):
        # , fg="white", bg="blue"
        labelWidget = Tkinter.Label(self.frame, text=label)
        labelWidget.grid(column=column, row=self.row)
        self.row += 1

    def defineLabel(self, label, column=0, incRow=False, **kwargs):
        labelWidget = Tkinter.Label(self.frame, text=label, **kwargs)
        labelWidget.grid(column=column, row=self.row, sticky='W')
        if incRow == True:
            self.row += 1

    def defineScale(self, value, label, from_, to, resolution, default, column=1, updateRow=True):
        if label is not None:
            self.defineLabel(label)
        var = Tkinter.Scale(self.frame, from_=from_, to=to,
                            resolution=resolution,
                            orient=Tkinter.HORIZONTAL)
        if value is not None:
            var.set(value)
        else:
            var.set(default)
        var.grid(column=column, row=self.row)

        if updateRow == True:
            self.row += 1
        return var

    def defineListbox(self, value, label, items):
        import os
        isMacosx = (os.name == 'mac' or os.name == 'posix')

        if label is not None:
            self.defineLabel(label)

        scrollbar = Tkinter.Scrollbar(self.frame, orient=Tkinter.VERTICAL)
        var = Tkinter.Listbox(self.frame, selectmode=Tkinter.SINGLE,
                              yscrollcommand=scrollbar.set, height=6)
        scrollbar.config(command=var.yview)
        scrollbar.grid(column=2, row=self.row)

        for item in items:
            var.insert(Tkinter.END, item)

        if value is not None:
            items = var.get(0, Tkinter.END)
            item  = value

            selection = 0
            for i in xrange(len(items)):
                if items[i] == item:
                    selection = i
                    break
            var.activate(selection)
            # this call make the listbox to be badly displayed under macosx.
            if not isMacosx:
                var.selection_set(selection)
        else:
            var.activate(0)
            if not isMacosx:
                var.selection_set(0)
        var.grid(column=1, row=self.row)

        self.row += 1
        return var

    def defineEntry(self, value, label, column=1, updateRow=True):
        if label is not None:
            self.defineLabel(label)

        var = Tkinter.Entry(self.frame)
        if value is not None:
            var.insert(Tkinter.INSERT, value)
        var.grid(column=column, row=self.row)

        if updateRow == True:
            self.row += 1
        return var

    def defineCheckbox(self, value, label, column=0, updateRow=True, default=0):
        var = Tkinter.IntVar()
        if value is not None:
            if value == 'true':
                var.set(1)
            else:
                var.set(0)
        else:
            var.set(default)

        if label is not None:
            button = Tkinter.Checkbutton(self.frame, text=label, variable=var)
        else:
            button = Tkinter.Checkbutton(self.frame, variable=var)
        button.grid(column=column, row=self.row, sticky='W')

        if updateRow == True:
            self.row += 1
        return var

    def isBoxChecked(self, box):
        if box.get() == 1:
            return 'true'
        else:
            return 'false'

    def defineBitmap(self):
        pass
    # BitmapImage
