import Tkinter
import Image, ImageTk
import tkFileDialog
import tkMessageBox
import tkColorChooser
from listAvailableElements import TEXTURES, EDGETEXTURES
from listAvailableElements import SPRITES, PARTICLESOURCES
import logging
from xmotoTools import alphabeticSortOfKeys, getExistingImageFullPath
from xmotoTools import dec2hex, hex2dec
from factory import Factory

class XmGui:
    def __init__(self):
        self.defaultBitmapSize = 92
        EDGETEXTURES['_None_'] = {'file':'none.png'}
        TEXTURES['_None_'] = {'file':'none.png'}
        SPRITES['_None_'] = {'file':'none.png'}
        self.callback = None
        self.savedFrame = None

    def newFrame(self):
        if self.savedFrame is None:
            self.savedFrame = self.frame
            self.frame = Tkinter.Frame(self.frame)

    def popFrame(self):
        if self.savedFrame is not None:
            self.frame.pack()

            self.frame = self.savedFrame
            self.savedFrame = None

    def defineWindowHeader(self, title=''):
        self.root = Tkinter.Tk()
        self.root.title(title)
        self.frame = Tkinter.Frame(self.root)
        self.frame.pack()

    def defineOkCancelButtons(self, command):
        self.ok_button = Tkinter.Button(self.frame, text="OK",
                                        command=command)
        self.ok_button.pack(side=Tkinter.RIGHT)

        self.cancel_button = Tkinter.Button(self.frame, text="Cancel",
                                            command=self.frame.quit)
        self.cancel_button.pack(side=Tkinter.RIGHT)


    def setSelectedBitmap(self, imgName, buttonName):
        self.top.destroy()
        if self.callback is not None:
            self.callback(imgName, buttonName)

    def textureSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Texture Selection', TEXTURES, buttonName)

    def edgeSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Edge Selection', EDGETEXTURES, buttonName)

    def spriteSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Sprite Selection', SPRITES, buttonName)

    def particleSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Particle Source Selection',
                                   PARTICLESOURCES, buttonName)


    def bitmapSelectionWindow(self, title, bitmaps, callingButton):
        self.top = Tkinter.Toplevel(self.root)
        self.top.title(title)
        scrollbarV = Tkinter.Scrollbar(self.top, orient=Tkinter.VERTICAL)
        scrollbarH = Tkinter.Scrollbar(self.top, orient=Tkinter.HORIZONTAL)
        canvas = Tkinter.Canvas(self.top,
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
                if imageFilename[0:2] == '__':
                    continue

                XmBitmap(frame, imageFilename, name,
                         command=self.setSelectedBitmap,
                         grid=(counter % 4, counter / 4),
                         buttonName=callingButton)
            except Exception, e:
                logging.info("Can't create XmBitmap from %s.\n%s"
                             % (imageFilename, e))
            else:
                counter += 1

        canvas.create_window(0, 0, window=frame)
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(0.0)
        canvas.xview_moveto(0.0)

        self.root.wait_window(self.top)

    def getBitmapSizeDependingOnScreenResolution(self):
        screenheight = self.frame.winfo_screenheight()
        bitmapSize   = self.defaultBitmapSize
        if screenheight <= 768:
            bitmapSize /= 2
        if screenheight <= 600:
            bitmapSize /= 2

        return bitmapSize

class XmWidget:
    def __init__(self):
        self.widget = None
        self.frame = None

    def show(self):
        if self.frame is not None:
            for child in self.frame.children.values():
                child.configure(state=Tkinter.NORMAL)
            
    def hide(self):
        if self.frame is not None:
            for child in self.frame.children.values():
                child.configure(state=Tkinter.DISABLED)

    def get(self):
        return self.widget.get()

class XmFileSelect(XmWidget):
    def __init__(self, top, value=None, label=None):
        XmWidget.__init__(self)
        selectionFrame = Tkinter.Frame(top)
        selectionFrame.pack(fill=Tkinter.X)

        if label is not None:
            XmLabel(selectionFrame, label, alone=False)

        button = Tkinter.Button(selectionFrame, text="open",
                                command=self.fileSelectCallback)
        button.pack(side=Tkinter.RIGHT)

        self.var = Tkinter.Entry(selectionFrame)
        if value is not None:
            self.var.insert(Tkinter.INSERT, value)
        self.var.pack(side=Tkinter.RIGHT)
        
    def fileSelectCallback(self):
        openFile = tkFileDialog.askopenfile(parent=xmGui.frame,
                                            mode='rb',
                                            title='Choose a file')
        if openFile is not None:
            openFile.close()
            self.var.delete(0, Tkinter.END)
            self.var.insert(Tkinter.INSERT, openFile.name)

    def get(self):
        return self.var.get()

class XmTitle(XmWidget):
    def __init__(self, top, label):
        XmWidget.__init__(self)
        titleFrame = Tkinter.Frame(top, relief=Tkinter.RAISED, borderwidth=1)
        titleFrame.pack(fill=Tkinter.X)

        labelWidget = Tkinter.Label(titleFrame, text=label)
        labelWidget.pack(fill=Tkinter.BOTH, expand=True)

class XmMessage(XmWidget):
    def __init__(self, top, msg):
        XmWidget.__init__(self)
        self.widget = Tkinter.Message(top, text=msg)
        self.widget.pack(fill=Tkinter.X)

class XmLabel(XmWidget):
    def __init__(self, top, label, alone=True, grid=None):
        XmWidget.__init__(self)
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

class XmListbox(XmWidget):
    def __init__(self, top, value, label, items):
        XmWidget.__init__(self)
        import os
        isMacosx = (os.name == 'mac' or os.name == 'posix')

        self.frame = Tkinter.Frame(top)
        self.frame.pack(fill=Tkinter.X)

        if label is not None:
            XmLabel(self.frame, label, alone=False)

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

class XmScale(XmWidget):
    def __init__(self, top, value, alone=True, **keywords):
        XmWidget.__init__(self)
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
            XmLabel(self.frame, label, alone=False)

        self.widget = Tkinter.Scale(self.frame, from_=from_, to=to,
                                    resolution=resolution,
                                    orient=Tkinter.HORIZONTAL)
        if value is not None:
            self.widget.set(value)
        else:
            self.widget.set(default)
        self.widget.pack(fill=Tkinter.X)

class XmCheckbox(XmWidget):
    def __init__(self, top, value, default=0, alone=True, **params):
        XmWidget.__init__(self)
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

class XmEntry(XmWidget):
    def __init__(self, top, value, label):
        XmWidget.__init__(self)
        self.frame = Tkinter.Frame(top)
        self.frame.pack(fill=Tkinter.X)

        if label is not None:
            XmLabel(self.frame, label, alone=False)

        self.widget = Tkinter.Entry(self.frame)
        if value is not None:
            self.widget.insert(Tkinter.INSERT, value)
        self.widget.pack(side=Tkinter.RIGHT)

class XmRadio(XmWidget):
    def __init__(self, top, value, buttons, label=None, command=None):
        XmWidget.__init__(self)
        frame = Tkinter.Frame(top)
        frame.pack(fill=Tkinter.X)

        if label is not None:
            XmLabel(frame, label, alone=False)

        self.var = Tkinter.StringVar()
        if value is not None:
            self.var.set(value)
        else:
            # default to the first button
            (text, value) = buttons[0]
            self.var.set(value)

        for text, value in buttons:
            b = Tkinter.Radiobutton(frame, text=text,
                                    variable=self.var, value=value,
                                    command=command)
            b.pack(side=Tkinter.LEFT)
        
    def get(self):
        return self.var.get()

class XmColor(XmWidget):
    """ inspired by ColorButton in BKchem """
    def __init__(self, top, r, g, b, label, grid=None, size=92):
        XmWidget.__init__(self)

        def colorFromRGB(r, g, b):
            def toHex(color):
                low = color & 15
                high = color >> 4
                return dec2hex(high) + dec2hex(low)

            color = '#' + toHex(r) + toHex(g) + toHex(b)
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

def getImage(imgName, bitmapDict=None, size=92):
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
            image   = Image.open(imgFileFullPath)
            image   = image.resize((size, size))
            tkImage = ImageTk.PhotoImage(image)
        except Exception, e:
            logging.warning("Can't create tk image from __missing__.png, \
looks like inksmoto has not been successfully installed.\n%s" % e)

    return tkImage

class XmBitmap(XmWidget):
    def __init__(self, top, filename, label, command=None,
                 toDisplay=None, callback=None,
                 grid=None, buttonName='', size=92):
        XmWidget.__init__(self)
        
        if callback is not None:
            xmGui.callback = callback

        self.frame = Tkinter.Frame(top)
        if grid is None:
            self.frame.pack()
        else:
            self.frame.grid(column=grid[0], row=grid[1])

        tkImage = getImage(filename, size=size)

        cmds = {'textures': xmGui.textureSelectionWindow,
                'edges': xmGui.edgeSelectionWindow,
                'sprites': xmGui.spriteSelectionWindow,
                'particlesources': xmGui.particleSelectionWindow}
        if toDisplay is not None:
            command = cmds[toDisplay]

        if tkImage is None:
            logging.info("tkImage [%s] is None" % filename)
            self.widget = Tkinter.Button(self.frame, text="Missing image",
                                         command=lambda: command(label,
                                                                 buttonName))
        else:
            # have to use a lambda function to pass parameters to the
            # callback function
            self.widget = Tkinter.Button(self.frame, image=tkImage,
                                         width=size, height=size,
                                         command=lambda: command(label,
                                                                 buttonName))
        self.widget.tkImage = tkImage
        self.widget.pack()

        self.label = Tkinter.Label(self.frame, text=label)
        self.label.pack()

        self.size = size

    def get(self):
        # ugly as fuck... but tkinter keeps the text there...
        return self.label.config()['text'][4]

    def update(self, imgName, bitmapDict):
        tkImage = getImage(imgName, bitmapDict, self.size)

        if tkImage is not None:
            self.widget.tkImage = tkImage
            self.widget.configure(image=tkImage)
        self.label.configure(text=imgName)

""" store the XmGui instance at module level """
xmGui = XmGui()

def quit():
    xmGui.frame.quit()

def mainLoop():
    xmGui.root.mainloop()

def defineWindowHeader(title):
    xmGui.defineWindowHeader(title)

def defineOkCancelButtons(command):
    xmGui.defineOkCancelButtons(command)

def newFrame():
    xmGui.newFrame()

def popFrame():
    xmGui.popFrame()

def errorMessageBox(msg):
    tkMessageBox.showerror('Error', msg)

def getBitmapSizeDependingOnScreenResolution():
    return xmGui.getBitmapSizeDependingOnScreenResolution()

# buttons availables from unit tests
def invokeOk():
    xmGui.ok_button.invoke()

def invokeCancel():
    xmGui.cancel_button.invoke()

def newXmFileSelect(*args, **kwargs):
    return XmFileSelect(xmGui.frame, *args, **kwargs)
def newXmTitle(*args, **kwargs):
    return XmTitle(xmGui.frame, *args, **kwargs)
def newXmMessage(*args, **kwargs):
    return XmMessage(xmGui.frame, *args, **kwargs)
def newXmLabel(*args, **kwargs):
    return XmLabel(xmGui.frame, *args, **kwargs)
def newXmListbox(*args, **kwargs):
    return XmListbox(xmGui.frame, *args, **kwargs)
def newXmScale(*args, **kwargs):
    return XmScale(xmGui.frame, *args, **kwargs)
def newXmCheckbox(*args, **kwargs):
    return XmCheckbox(xmGui.frame, *args, **kwargs)
def newXmEntry(*args, **kwargs):
    return XmEntry(xmGui.frame, *args, **kwargs)
def newXmRadio(*args, **kwargs):
    return XmRadio(xmGui.frame, *args, **kwargs)
def newXmColor(*args, **kwargs):
    return XmColor(xmGui.frame, *args, **kwargs)
def newXmBitmap(*args, **kwargs):
    return XmBitmap(xmGui.frame, *args, **kwargs)

Factory().registerObject('XmFileSelect', newXmFileSelect)
Factory().registerObject('XmTitle', newXmTitle)
Factory().registerObject('XmMessage', newXmMessage)
Factory().registerObject('XmLabel', newXmLabel)
Factory().registerObject('XmListbox', newXmListbox)
Factory().registerObject('XmScale', newXmScale)
Factory().registerObject('XmCheckbox', newXmCheckbox)
Factory().registerObject('XmEntry', newXmEntry)
Factory().registerObject('XmRadio', newXmRadio)
Factory().registerObject('XmColor', newXmColor)
Factory().registerObject('XmBitmap', newXmBitmap)
