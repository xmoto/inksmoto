from xmotoExtension import XmotoExtension
from xmotoTools import alphabeticSortOfKeys, getExistingImageFullPath, createIfAbsent, applyOnElements
from inkex import addNS, NSS
from lxml import etree
from lxml.etree import Element
from os.path import join
import Tkinter
import Image, ImageTk
import tkFileDialog
import tkMessageBox
import tkColorChooser
import logging, log
from listAvailableElements import textures, edgeTextures, sprites, particleSources

class XmotoWidget:
    def __init__(self):
        pass

    def show(self):
        for child in self.frame.children.values():
            child.configure(state=Tkinter.NORMAL)
            
    def hide(self):
        for child in self.frame.children.values():
            child.configure(state=Tkinter.DISABLED)

    def get(self):
        return self.widget.get()

class XmotoLabel(XmotoWidget):
    def __init__(self, top, label, alone=True, grid=None):
        self.widget = Tkinter.Label(top, text=label)
        if grid is not None:
            self.widget.grid(column=grid[0], row=grid[1])
        else:
            if alone == True:
                self.widget.pack(anchor=Tkinter.W)
            else:
                self.widget.pack(side=Tkinter.LEFT)

    def show(self):
        self.widget.configure(state=Tkinter.NORMAL)

    def hide(self):
        self.widget.configure(state=Tkinter.DISABLED)

class XmotoListbox(XmotoWidget):
    def __init__(self, top, value, label, items):
        import os
        isMacosx = (os.name == 'mac' or os.name == 'posix')

        self.frame = Tkinter.Frame(top)
        self.frame.pack(fill=Tkinter.X)

        if label is not None:
            XmotoLabel(self.frame, label, alone=False)

        scrollbar = Tkinter.Scrollbar(self.frame, orient=Tkinter.VERTICAL)
        self.widget = Tkinter.Listbox(self.frame, selectmode=Tkinter.SINGLE,
                              yscrollcommand=scrollbar.set, height=6)
        scrollbar.config(command=self.widget.yview)
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        for item in items:
            self.widget.insert(Tkinter.END, item)

        if value is not None:
            items = self.widget.get(0, Tkinter.END)
            item  = value

            selection = 0
            for i in xrange(len(items)):
                if items[i] == item:
                    selection = i
                    break
            self.widget.activate(selection)
            # this call make the listbox to be badly displayed under macosx.
            if not isMacosx:
                self.widget.selection_set(selection)
        else:
            self.widget.activate(0)
            if not isMacosx:
                self.widget.selection_set(0)
        self.widget.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH)

    def get(self):
        return self.widget.get(Tkinter.ACTIVE)

class XmotoScale(XmotoWidget):
    def __init__(self, top, value, alone=True, **keywords):
        label = keywords['label']
        from_ = keywords['from_']
        to    = keywords['to']
        resolution = keywords['resolution']
        default = keywords['default']

        self.frame = Tkinter.Frame(top)
        if alone == True:
            self.frame.pack(fill=Tkinter.X)
        else:
            self.frame.pack(side=Tkinter.LEFT)

        if label is not None:
            XmotoLabel(self.frame, label, alone=False)

        self.widget = Tkinter.Scale(self.frame, from_=from_, to=to,
                                    resolution=resolution,
                                    orient=Tkinter.HORIZONTAL)
        if value is not None:
            self.widget.set(value)
        else:
            self.widget.set(default)
        self.widget.pack(fill=Tkinter.X)

class XmotoCheckBox(XmotoWidget):
    def __init__(self, top, value, default=0, alone=True, **params):
        self.var = Tkinter.IntVar()
        if value is not None:
            if value == 'true':
                self.var.set(1)
            else:
                self.var.set(0)
        else:
            self.var.set(default)

        params['variable'] = self.var

        self.frame = Tkinter.Frame(top)
        if alone == True:
            self.frame.pack(fill=Tkinter.X)
        else:
            self.frame.pack(side=Tkinter.LEFT)

        self.widget = Tkinter.Checkbutton(self.frame, **params)
        self.widget.pack(fill=Tkinter.X)

    def get(self):
        return self.var.get()

class XmotoEntry(XmotoWidget):
    def __init__(self, top, value, label):
        self.frame = Tkinter.Frame(top)
        self.frame.pack(fill=Tkinter.X)

        if label is not None:
            XmotoLabel(self.frame, label, alone=False)

        self.widget = Tkinter.Entry(self.frame)
        if value is not None:
            self.widget.insert(Tkinter.INSERT, value)
        self.widget.pack(side=Tkinter.RIGHT)

class XmotoColorButton(XmotoWidget):
    """ inspired by ColorButton in BKchem """
    def __init__(self, top, r, g, b, label, grid=None, size=92):
        def colorFromRGB(r, g, b):
            color = hex(b + (g<<8) + (r<<16))
            color = '#' + color[2:]
            return color

        def getWidthHeightFromSize(size):
            """ as we do not display a bitmap, we can't use the pixel size,
                instead, we have to use text size...
                pretty ugly as shit...
                maybe there's a nice conversion function in tkinter... """
            if size == 92:
                return (10, 6)
            elif size == 46:
                return (4, 3)
            elif size == 23:
                return (1, 1)
            else:
                return (10, 6)

        self.rgb = (r, g, b)
        color = colorFromRGB(r, g, b)
        self.setColor(color)

        self.frame = Tkinter.Frame(top)
        if grid is None:
            self.frame.pack()
        else:
            self.frame.grid(column=grid[0], row=grid[1])

        (w, h) = getWidthHeightFromSize(size)
        self.widget = Tkinter.Button(self.frame,
                                     background=self.color,
                                     activebackground=self.color,
                                     command=self._selectColor,
                                     width=w, height=h)
        self.widget.pack()

        self.label = Tkinter.Label(self.frame, text=label)
        self.label.pack()

    def get(self):
        return self.rgb

    def setColor(self, color):
        self.color = color

    def _selectColor(self):
        if self.color is not None:
          color = tkColorChooser.askcolor(self.color)
        else:
          color = tkColorChooser.askcolor()
        if color[1]:
          self.setColor(color[1])
          self.rgb = color[0]
          self.widget.configure(background=self.color,
                                activebackground=self.color)

class XmotoBitmap(XmotoWidget):
    def __init__(self, top, filename, label, command, grid=None, buttonName='', size=92):
        self.frame = Tkinter.Frame(top)
        if grid is None:
            self.frame.pack()
        else:
            self.frame.grid(column=grid[0], row=grid[1])

        tkImage = self.getImage(filename, size=size)

        if tkImage is None:
            logging.info("tkImage [%s] is None" % filename)
            self.widget = Tkinter.Button(self.frame, text="Missing image",
                                         command=lambda : command(label, buttonName))
        else:
            # have to use a lambda function to pass parameters to the callback function
            self.widget = Tkinter.Button(self.frame, image=tkImage,
                                         width=size, height=size,
                                         command=lambda : command(label, buttonName))
        self.widget.tkImage = tkImage
        self.widget.pack()

        self.label = Tkinter.Label(self.frame, text=label)
        self.label.pack()

    def get(self):
        # ugly as fuck... but tkinter keeps the text there...
        return self.label.config()['text'][4]

    def update(self, imgName, bitmapDict):
        tkImage = self.getImage(imgName, bitmapDict)

        if tkImage is not None:
            self.widget.tkImage = tkImage
            self.widget.configure(image=tkImage)
        self.label.configure(text=imgName)

    def getImage(self, imgName, bitmapDict=None, size=92):
        tkImage = None

        try:
            if bitmapDict is not None:
                imgName = bitmapDict[imgName]['file']

            imgFileFullPath = getExistingImageFullPath(imgName)
            image   = Image.open(imgFileFullPath)
            image   = image.resize((size, size))
            tkImage = ImageTk.PhotoImage(image)
        except Exception, e:
            logging.info("Can't create tk image from %s\n%s" % (imgName, e))
            try:
                imgFileFullPath = getExistingImageFullPath('__missing__.png')
                image   = image.resize((size, size))
                image   = Image.open(imgFileFullPath)
                tkImage = ImageTk.PhotoImage(image)
            except Exception, e:
                logging.warning("Can't create tk image from __missing__.png, looks like inksmoto has not been successfully installed.\n%s" % e)
                pass

        return tkImage

class XmotoExtensionTkinter(XmotoExtension):
    """ for extensions with their own window made with tkinter
    """
    def __init__(self):
        XmotoExtension.__init__(self)
        edgeTextures['_None_'] = {'file':'none.png'}
        textures['_None_']     = {'file':'none.png'}
        sprites['_None_']      = {'file':'none.png'}
        self.defaultBitmapSize = 92

    def defineWindowHeader(self, title=''):
        self.root = Tkinter.Tk()
        self.root.title(title)
        self.frame = Tkinter.Frame(self.root)
        self.frame.pack()

    def defineOkCancelButtons(self, top, command):
        self.ok_button = Tkinter.Button(top, text="OK", command=command)
        self.ok_button.pack(side=Tkinter.RIGHT)

        self.cancel_button = Tkinter.Button(top, text="Cancel", command=top.quit)
        self.cancel_button.pack(side=Tkinter.RIGHT)

    def defineTitle(self, top, label):
        titleFrame = Tkinter.Frame(top, relief=Tkinter.RAISED, borderwidth=1)
        titleFrame.pack(fill=Tkinter.X)

        labelWidget = Tkinter.Label(titleFrame, text=label)
        labelWidget.pack(fill=Tkinter.BOTH, expand=True)

    def defineLabel(self, top, label, alone=True, grid=None):
        labelWidget = Tkinter.Label(top, text=label)
        if grid is not None:
            labelWidget.grid(column=grid[0], row=grid[1])
        else:
            if alone == True:
                labelWidget.pack(anchor=Tkinter.W)
            else:
                labelWidget.pack(side=Tkinter.LEFT)

        return labelWidget

    def defineMessage(self, top, msg):
        msgWidget = Tkinter.Message(top, text=msg)
        msgWidget.pack(fill=Tkinter.X)

    def isBoxChecked(self, box):
        if box.get() == 1:
            return 'true'
        else:
            return 'false'

    def fileSelectHook(self, filename):
        pass

    def fileSelectCallback(self):
        openFile = tkFileDialog.askopenfile(parent=self.frame,
                                            mode='rb',
                                            title='Choose a file')
        if openFile is not None:
            openFile.close()
            self.fileSelectHook(openFile.name)

    def defineFileSelectDialog(self, top, value=None, label=None):
        selectionFrame = Tkinter.Frame(top)
        selectionFrame.pack(fill=Tkinter.X)

        if label is not None:
            self.defineLabel(selectionFrame, label, alone=False)

        button = Tkinter.Button(selectionFrame, text="open", command=self.fileSelectCallback)
        button.pack(side=Tkinter.RIGHT)

        var = Tkinter.Entry(selectionFrame)
        if value is not None:
            var.insert(Tkinter.INSERT, value)
        var.pack(side=Tkinter.RIGHT)

        return var

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        pass

    def setSelectedBitmap(self, imgName, buttonName):
        self.top.destroy()
        self.bitmapSelectionWindowHook(imgName, buttonName)

    def textureSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Texture Selection', textures, buttonName)

    def edgeSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Edge Selection', edgeTextures, buttonName)

    def spriteSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Sprite Selection', sprites, buttonName)

    def particleSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Particle Source Selection', particleSources, buttonName)

    def bitmapSelectionWindow(self, title, bitmaps, callingButton):
        self.top = Tkinter.Toplevel(self.root)
        self.top.title(title)
        scrollbarV = Tkinter.Scrollbar(self.top, orient=Tkinter.VERTICAL)
        scrollbarH = Tkinter.Scrollbar(self.top, orient=Tkinter.HORIZONTAL)
        canvas     = Tkinter.Canvas(self.top,
                                    yscrollcommand=scrollbarV.set,
                                    xscrollcommand=scrollbarH.set,
                                    width=512+32, height=512)
        canvas.grid(row=0, column=0, sticky="news")

        scrollbarV.config(command=canvas.yview)
        scrollbarV.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S)
        scrollbarH.config(command=canvas.xview)
        scrollbarH.grid(row=1, column=0, sticky=Tkinter.E+Tkinter.W)

        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_columnconfigure(0, weight=1)

        frame = Tkinter.Frame(canvas)

        counter = 0
        keys = alphabeticSortOfKeys(bitmaps.keys())
        for name in keys:
            imageFilename = bitmaps[name]['file']

            try:
                XmotoBitmap(frame, imageFilename, name,
                            command=self.setSelectedBitmap,
                            grid=(counter % 4, counter / 4),
                            buttonName=callingButton)
            except Exception, e:
                logging.info("Can't create XmotoBitmap from %s.\n%s" % (imageFilename, e))
                pass
            else:
                counter += 1

        canvas.create_window(0, 0, window=frame)
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(0.0)
        canvas.xview_moveto(0.0)

        self.root.wait_window(self.top)

    def defineRadioButtons(self, top, value, buttons, label=None, command=None):
        frame = Tkinter.Frame(top)
        frame.pack(fill=Tkinter.X)

        if label is not None:
            self.defineLabel(frame, label, alone=False)

        var = Tkinter.StringVar()
        if value is not None:
            var.set(value)
        else:
            # default to the first button
            (text, value) = buttons[0]
            var.set(value)

        for text, value in buttons:
            b = Tkinter.Radiobutton(frame, text=text,
                                    variable=var, value=value,
                                    command=command)
            b.pack(side=Tkinter.LEFT)

        return var

    def getBitmapSizeDependingOnScreenResolution(self):
        screenheight = self.frame.winfo_screenheight()
        bitmapSize   = self.defaultBitmapSize
        if screenheight <= 768:
            bitmapSize /= 2
        if screenheight <= 600:
            bitmapSize /= 2

        return bitmapSize

class XmotoExtTkLevel(XmotoExtensionTkinter):
    """ update level's properties
    """
    def setMetaData(self):
        try:
            self.updateLabelData()
        except Exception, e:
            tkMessageBox.showerror('Error', e)
            return

        self.frame.quit()

        self.unparseLabel()

        if self.description is not None:
            self.description.text = self.labelValue
        else:
            self.createMetadata(self.labelValue)

    def effect(self):
        (self.description, self.labelValue) = self.getMetaData()
        self.parseLabel(self.labelValue)

        self.createWindow()
        self.defineOkCancelButtons(self.frame, command=self.setMetaData)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
        else:
            self.root.mainloop()

        self.afterHook()

    def afterHook(self):
        pass

    def createWindow(self):
        pass

class XmotoExtTkElement(XmotoExtensionTkinter):
    """ update elements' properties
    """
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)
        # the dictionnary which contains the elements informations
        self.commonValues = {}
        self.namespacesInCommon = None
        self.originalValues = {}

    def addPath(self, path):
        # put None if a value is different in at least two path
        xmotoLabel = path.get(addNS('xmoto_label', 'xmoto'), '')
        self.parseLabel(xmotoLabel)

        elementId = path.get('id', '')
        for name, value in self.label.iteritems():
            if type(value) == dict:
                namespace    = name
                namespaceDic = value

                # save original xmotoLabel to put back parameters not modified by this extension
                if self.namespacesInCommon is not None and namespace not in self.namespacesInCommon:
                    createIfAbsent(self.originalValues, elementId)
                    createIfAbsent(self.originalValues[elementId], namespace)
                    for var, value in namespaceDic.iteritems():
                        self.originalValues[elementId][namespace][var] = value
                    continue

                if namespace not in self.commonValues:
                    self.commonValues[namespace] = {}

                for (name, value) in namespaceDic.iteritems():
                    if name in self.commonValues[namespace]:
                        if self.commonValues[namespace][name] != value:
                            self.commonValues[namespace][name] = None
                    else:
                        self.commonValues[namespace][name] = value;
            else:
                if name in self.commonValues:
                    if self.commonValues[name] != value:
                        self.commonValues[name] = None
                else:
                    self.commonValues[name] = value;

    def updateContent(self, element):
        elementId = element.get('id', '')

        if elementId in self.originalValues:
            savedLabel = self.label.copy()
            for namespace, namespaceDic in self.originalValues[elementId].iteritems():
                createIfAbsent(self.label, namespace)
                for var, value in namespaceDic.iteritems():
                    self.label[namespace][var] = value

        self.unparseLabel()


        self.generateStyle()
        self.unparseStyle()

        self.updateNodeSvgAttributes(element)

        if elementId in self.originalValues:
            self.label = savedLabel.copy()

    def okPressed(self):
        try:
            self.label = self.getUserChanges()
        except Exception, e:
            tkMessageBox.showerror('Error', e)
            return
  
        applyOnElements(self, self.selected, self.updateContent)

        self.frame.quit()

    def effect(self):
        if len(self.selected) == 0:
            return

        applyOnElements(self, self.selected, self.addPath)

        self.createWindow()
        self.defineOkCancelButtons(self.frame, command=self.okPressed)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
        else:
            self.root.mainloop()

    # the two methods to implement in child
    def createWindow(self):
        pass

    def getUserChanges(self):
        pass
