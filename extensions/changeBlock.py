from xmotoExtensionTkinter import XmotoExtensionTkinter
from xmotoExtension import getInkscapeExtensionsDir
from inkex import NSS, addNS
from os.path import join
import logging, log
import Tkinter
import Image, ImageTk
from listAvailableElements import textures, edgeTextures


class ChangeBlock(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)
        self.commonValues = {}
        edgeTextures['_None_'] = 'none.png'
        textures['_None_']     = 'none.png'
        self.defaultGrip  = 20.0
        self.defaultAngle = 270.0

    def addPath(self, path):
        # put None if a value is different in at least two path
        self.parseLabel(path.get(addNS('xmoto_label', 'xmoto'), ''))

        for name, value in self.label.iteritems():
            if type(value) == dict:
                namespace    = name
                namespaceDic = value
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
        self.unparseLabel()
        element.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())

        self.generateStyle()
        self.unparseStyle()
        element.set('style', self.getStyleValue())

    def getBitmapNameFromButtonName(self, buttonName):
        values = self.__dict__[buttonName].children.values()

        for child in values:
            if child.winfo_class() == 'Label':
                # ugly as fuck... but tkinter keeps the text there...
                return child.config()['text'][4]

    def getUserChanges(self):
        def createIfAbsent(dict, key):
            if not key in dict:
                dict[key] = {}
            
        def delWithoutExcept(dict, value):
            try:
                del dict[value]
            except:
                pass

        def setOrDelBool(dict, key):
            if self.__dict__[key].get() == 1:
                dict[key] = 'true'
            else:
                delWithoutExcept(dict, key)

        def setOrDelBitmap(dict, key, buttonName, silent=True):
            bitmapName = self.getBitmapNameFromButtonName(buttonName)
            if bitmapName not in ['_None_', '', None, 'None']:
                dict[key] = bitmapName
            else:
                if silent == True:
                    delWithoutExcept(dict, key)
                else:
                    raise Exception('%s is not defined' % key)

        # handle texture
        createIfAbsent(self.commonValues, 'usetexture')
        setOrDelBitmap(self.commonValues['usetexture'], 'id', 'texFrame', silent=False)

        # handle position
        createIfAbsent(self.commonValues, 'position')
        setOrDelBool(self.commonValues['position'], 'background')
        setOrDelBool(self.commonValues['position'], 'dynamic')

        # handle edges
        createIfAbsent(self.commonValues, 'edge')
        createIfAbsent(self.commonValues, 'edges')

        self.commonValues['edges']['method'] = self.drawMethod.get()
        if self.drawMethod.get()   in ['angle']:
            self.angle.configure(state=Tkinter.NORMAL)
            setStateOfChildren(self.downEdge,   Tkinter.NORMAL)
            setStateOfChildren(self.angleFrame, Tkinter.NORMAL)
        elif self.drawMethod.get() in ['in', 'out']:
            self.angle.configure(state=Tkinter.DISABLED)
            setStateOfChildren(self.downEdge,   Tkinter.DISABLED)
            setStateOfChildren(self.angleFrame, Tkinter.DISABLED)

        setOrDelBitmap(self.commonValues['edge'], 'texture',     'upperEdge')
        setOrDelBitmap(self.commonValues['edge'], 'downtexture', 'downEdge')

        return self.commonValues

    def okPressed(self):
        #try:
        self.label = self.getUserChanges()
        #except:
        #    return
        
        for self.id, element in self.selected.iteritems():
            if element.tag in [addNS('path', 'svg'), addNS('rect', 'svg')]:
		self.updateContent(element)
	    elif element.tag in [addNS('g', 'svg')]:
		# get elements in the group
		for subelement in element.xpath('./svg:path|./svg:rect', NSS):
		    self.updateContent(subelement)

        self.frame.quit()

    def effect(self):
        if len(self.selected) == 0:
            return

        for self.id, element in self.selected.iteritems():
            if element.tag in [addNS('path', 'svg'), addNS('rect', 'svg')]:
		self.addPath(element)
	    elif element.tag in [addNS('g', 'svg')]:
		# get elements in the group
		for subelement in element.xpath('./svg:path|./svg:rect', NSS):
		    self.addPath(subelement)

        self.defineWindowHeader(title='Block properties')

        # texture
        self.defineTitle(self.frame, "Texture")
        self.defineLabel(self.frame, "Click the texture to choose another one.")
        defaultTexture = self.getValue('usetexture', 'id', self.commonValues, default='_None_')
        self.texFrame  = self.defineBitmap(self.frame, textures[defaultTexture], defaultTexture, self.textureSelectionWindow, buttonName='texFrame')

        # type
        self.defineTitle(self.frame, "Type")
        self.defineLabel(self.frame, "Uncheck both to convert into normal block.")
        self.background = self.defineCheckbox(self.frame, self.getValue('position', 'background', self.commonValues), label='Convert in background block')
        self.dynamic    = self.defineCheckbox(self.frame, self.getValue('position', 'dynamic',    self.commonValues), label='Convert in dynamic block')

        # edges
        self.defineTitle(self.frame, "Edge")

        self.defineLabel(self.frame, "There can be up to two different edge textures for a block.")
        self.defineLabel(self.frame, "One for the upper side of the block, and another for the down side of the block.")
        self.defineLabel(self.frame, "")
        self.defineLabel(self.frame, "The edge drawing behaviour:")
        buttons = [('using the given angle', 'angle'), ('inside the block', 'in'), ('outside the block', 'out')]
        self.drawMethod = self.defineRadioButtons(self.frame, self.getValue('edges', 'drawmethod', self.commonValues, default='angle'),
                                                  buttons, command=self.edgeDrawCallback)

        self.edgeFrame = Tkinter.Frame(self.frame)
        defaultEdge    = self.getValue('edge', 'texture', self.commonValues, default='_None_')
        self.defineLabel(self.edgeFrame, "Upper edge texture", grid=(0, 0))
        self.upperEdge = self.defineBitmap(self.edgeFrame, edgeTextures[defaultEdge], defaultEdge, self.edgeSelectionWindow, grid=(0, 1), buttonName='upperEdge')

        defaultDownEdge= self.getValue('edge', 'downtexture', self.commonValues, default='_None_')
        self.downEdgeLabel = self.defineLabel(self.edgeFrame, "Down edge texture", grid=(1, 0))
        self.downEdge  = self.defineBitmap(self.edgeFrame, edgeTextures[defaultDownEdge], defaultDownEdge, self.edgeSelectionWindow, grid=(1, 1), buttonName='downEdge')

        self.edgeFrame.pack()

        self.angleLabel = self.defineLabel(self.frame, "The angle the edges point to (defaulted to 270.0):")
        (self.angle, self.angleFrame) = self.defineScale(self.frame, self.getValue('edges', 'angle', self.commonValues, default=self.defaultAngle), label='Edge angle', from_=0, to=360, resolution=1, default=self.defaultAngle)

        # physic
        self.defineTitle(self.frame, "Physic")
        self.defineLabel(self.frame, "The bigger the value, the bigger the grip.")
        self.defineLabel(self.frame, "Default value in Xmoto is 20.0")
        (self.grip, dummy) = self.defineEntry(self.frame, self.getValue('physics', 'grip', self.commonValues, default=self.defaultGrip), label='Block grip')

        self.defineOkCancelButtons(self.frame, command=self.okPressed)
        self.root.mainloop()

    def edgeDrawCallback(self):
        def setStateOfChildren(widget, state):
            for child in widget.children.values():
                child.configure(state=state)

        if self.drawMethod.get()   in ['angle']:
            self.angleLabel.configure(state=Tkinter.NORMAL)
            self.angle.configure(state=Tkinter.NORMAL)
            self.downEdgeLabel.configure(state=Tkinter.NORMAL)
            setStateOfChildren(self.downEdge,   Tkinter.NORMAL)
            setStateOfChildren(self.angleFrame, Tkinter.NORMAL)
        elif self.drawMethod.get() in ['in', 'out']:
            self.angleLabel.configure(state=Tkinter.DISABLED)
            self.angle.configure(state=Tkinter.DISABLED)
            self.downEdgeLabel.configure(state=Tkinter.DISABLED)
            setStateOfChildren(self.downEdge,   Tkinter.DISABLED)
            setStateOfChildren(self.angleFrame, Tkinter.DISABLED)

    def textureSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Texture Selection', textures, buttonName)

    def edgeSelectionWindow(self, imgName, buttonName):
        self.bitmapSelectionWindow('Edge Selection', edgeTextures, buttonName)

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        if buttonName in ['texFrame']:
            bitmapDict = textures
        elif buttonName in ['downEdge', 'upperEdge']:
            bitmapDict = edgeTextures

        imgFilename = join(getInkscapeExtensionsDir(), "xmoto_bitmap", bitmapDict[imgName])

        image   = Image.open(imgFilename)
        tkImage = ImageTk.PhotoImage(image)

        values = self.__dict__[buttonName].children.values()

        for child in values:
            if child.winfo_class() == 'Button':
                child.tkImage = tkImage
                child.configure(image=tkImage)
            elif child.winfo_class() == 'Label':
                child.configure(text=imgName)

e = ChangeBlock()
e.affect()
