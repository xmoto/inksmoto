from xmotoExtension import XmotoExtension
from inkex   import NSS
import xml.dom.Element
import xml.dom.Text
import Tkinter
import logging, log

class XmotoExtensionTkinter(XmotoExtension):
    """ use for extensions with their own window made with tkinter
    """
    def __init__(self):
        XmotoExtension.__init__(self)
        self.row = 1

    def getMetaData(self):
        self.labelValue = ""
        self.child = None
        descriptions = self.document.getElementsByTagNameNS(NSS['dc'], 'description')
        if len(descriptions) > 0:
            description = descriptions[0]
            if len(description.childNodes) > 0:
                child = description.childNodes[0]
                if child.nodeType == child.TEXT_NODE:
                    self.child = child
                    self.labelValue = child.data

        self.parseLabel(self.labelValue)

    def setMetaData(self):
        self.updateLabelData()

        self.frame.quit()

        self.unparseLabel()

        if self.child is not None:
            self.child.data = self.labelValue
        else:
            self.createMetada()

    def createMetada(self):
        self.svg  = self.document.getElementsByTagName('svg')[0]

        # create only dc:description or metadata/RDF/dc:description ?
        metadatas = self.document.getElementsByTagName('metadata')
        if len(metadatas) == 0:
            metadata = xml.dom.Element.Element(self.svg.ownerDocument, 'metadata')
            metadata.setAttribute('id', 'metadatasvg2lvl')
            self.svg.appendChild(metadata)
        else:
            metadata = metadatas[0]

        rdfs = metadata.getElementsByTagNameNS(NSS['rdf'], 'RDF')
        if len(rdfs) == 0:
            rdf = xml.dom.Element.Element(self.svg.ownerDocument, 'RDF',
                                          NSS['rdf'], None, None)
            metadata.appendChild(rdf)
        else:
            rdf = rdfs[0]

        works = rdf.getElementsByTagNameNS(NSS['cc'], 'Work')
        if len(works) == 0:            
            work = xml.dom.Element.Element(self.svg.ownerDocument, 'Work',
                                           NSS['cc'], None, None)
            work.setAttribute('rdf:about', '')
            rdf.appendChild(work)
        else:
            work = works[0]

        formats = work.getElementsByTagNameNS(NSS['dc'], 'format')
        if len(formats) == 0:
            format = xml.dom.Element.Element(self.svg.ownerDocument, 'format',
                                             NSS['dc'], None, None)
            formatText = xml.dom.Text.Text(self.svg.ownerDocument,
                                           'image/svg+xml')
            format.appendChild(formatText)
            work.appendChild(format)

        types = work.getElementsByTagNameNS(NSS['dc'], 'type')
        if len(types) == 0:
            typeNode = xml.dom.Element.Element(self.svg.ownerDocument, 'type',
                                           NSS['dc'], None, None)
            typeNode.setAttribute('rdf:resource', 'http://purl.org/dc/dcmitype/StillImage')
            work.appendChild(typeNode)


        description = xml.dom.Element.Element(self.svg.ownerDocument, 'description',
                                              NSS['dc'], None, None)
        descriptionText = xml.dom.Text.Text(self.svg.ownerDocument,
                                            self.labelValue)
        description.appendChild(descriptionText)
        work.appendChild(description)

    def defineOkCancelButtons(self):
        cancel_button = Tkinter.Button(self.frame, text="Cancel", command=self.frame.quit)
        cancel_button.grid(column=0, row=self.row)

        ok_button = Tkinter.Button(self.frame, text="OK", command=self.setMetaData)
        ok_button.grid(column=1, row=self.row)

    def defineLabel(self, label, column=0, incRow=False):
        labelWidget = Tkinter.Label(self.frame, text=label)
        labelWidget.grid(column=column, row=self.row)
        if incRow == True:
            self.row += 1

    def defineScale(self, domain, name, label, from_, to, resolution, default, column=1, updateRow=True):
        if label is not None:
            self.defineLabel(label)
        var = Tkinter.Scale(self.frame, from_=from_, to=to,
                            resolution=resolution,
                            orient=Tkinter.HORIZONTAL)
        if self.label[domain].has_key(name):
            var.set(self.label[domain][name])
        else:
            var.set(default)
        var.grid(column=column, row=self.row)

        if updateRow == True:
            self.row += 1
        return var

    def defineListbox(self, domain, name, label, items):
        if label is not None:
            self.defineLabel(label)

        scrollbar = Tkinter.Scrollbar(self.frame, orient=Tkinter.VERTICAL)
        var = Tkinter.Listbox(self.frame, selectmode=Tkinter.SINGLE,
                              yscrollcommand=scrollbar.set, height=6)
        scrollbar.config(command=var.yview)
        scrollbar.grid(column=2, row=self.row)

        for item in items:
            var.insert(Tkinter.END, item)

        if self.label[domain].has_key(name):
            items = var.get(0, Tkinter.END)
            item  = self.label[domain][name]

            selection = 0
            for i in xrange(len(items)):
                if items[i] == item:
                    selection = i
                    break
            var.activate(selection)
            var.selection_set(selection)
        else:
            var.activate(0)
            var.selection_set(0)
        var.grid(column=1, row=self.row)

        self.row += 1
        return var

    def defineEntry(self, domain, name, label, column=1, updateRow=True):
        if label is not None:
            self.defineLabel(label)

        var = Tkinter.Entry(self.frame)
        if self.label[domain].has_key(name):
            var.insert(Tkinter.INSERT, self.label[domain][name])
        var.grid(column=column, row=self.row)

        if updateRow == True:
            self.row += 1
        return var

    def defineCheckbox(self, domain, name, label, column=0, updateRow=True, default=0):
        var = Tkinter.IntVar()
        if self.label[domain].has_key(name):
            if self.label[domain][name] == 'true':
                var.set(1)
            else:
                var.set(0)
        else:
            var.set(default)

        if label is not None:
            button = Tkinter.Checkbutton(self.frame, text=label, variable=var)
        else:
            button = Tkinter.Checkbutton(self.frame, variable=var)
        button.grid(column=column, row=self.row)

        if updateRow == True:
            self.row += 1
        return var

    def isBoxChecked(self, box):
        if box.get() == 1:
            return 'true'
        else:
            return 'false'
