from xmotoExtensionTkinter import XmotoExtensionTkinter, XmotoListbox, XmotoScale, XmotoEntry, XmotoBitmap, XmotoLabel
from xmotoTools import getInkscapeExtensionsDir, getValue, createIfAbsent, delWithoutExcept
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

    def getUserChanges(self):
        def setOrDelBool(dict, widget, key):
            if widget.get() == 1:
                dict[key] = 'true'
            else:
                delWithoutExcept(dict, key)

        def setOrDelBitmap(dict, key, button, silent=True):
            bitmapName = button.get()
            if bitmapName not in ['_None_', '', None, 'None']:
                dict[key] = bitmapName
            else:
                if silent == True:
                    delWithoutExcept(dict, key)
                else:
                    raise Exception('%s is not defined' % bitmapName)

        # handle texture
        createIfAbsent(self.commonValues, 'usetexture')
        setOrDelBitmap(self.commonValues['usetexture'], 'id', self.texture, silent=False)

        # handle position
        createIfAbsent(self.commonValues, 'position')
        setOrDelBool(self.commonValues['position'], self.background, 'background')
        setOrDelBool(self.commonValues['position'], self.dynamic,    'dynamic')

        # handle edges
        createIfAbsent(self.commonValues, 'edge')
        createIfAbsent(self.commonValues, 'edges')

        self.commonValues['edges']['drawmethod'] = self.drawMethod.get()
        if self.drawMethod.get() in ['angle']:
            self.commonValues['edges']['angle'] = self.angle.get()

            setOrDelBitmap(self.commonValues['edge'], 'texture',     self.upperEdge)
            setOrDelBitmap(self.commonValues['edge'], 'downtexture', self.downEdge)

            # no edge texture selected
            if 'texture' not in self.commonValues['edge'] and 'downtexture' not in self.commonValues['edge']:
                delWithoutExcept(self.commonValues, 'edge')
                delWithoutExcept(self.commonValues, 'edges')

        elif self.drawMethod.get() in ['in', 'out']:
            delWithoutExcept(self.commonValues['edges'], 'angle')
            delWithoutExcept(self.commonValues['edge'],  'downtexture')
            setOrDelBitmap(self.commonValues['edge'], 'texture', self.upperEdge)

            # no edge texture selected
            if 'texture' not in self.commonValues['edge']:
                delWithoutExcept(self.commonValues, 'edge')
                delWithoutExcept(self.commonValues, 'edges')

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
        defaultTexture  = getValue(self.commonValues, 'usetexture', 'id', default='_None_')
        self.texture = XmotoBitmap(self.frame, textures[defaultTexture], defaultTexture, self.textureSelectionWindow, buttonName='texture')

        # type
        self.defineTitle(self.frame, "Type")
        self.defineLabel(self.frame, "Uncheck both to convert into normal block.")
        self.background = self.defineCheckbox(self.frame, getValue(self.commonValues, 'position', 'background'), label='Convert in background block')
        self.dynamic    = self.defineCheckbox(self.frame, getValue(self.commonValues, 'position', 'dynamic'),    label='Convert in dynamic block')

        # edges
        self.defineTitle(self.frame, "Edge")

        self.defineLabel(self.frame, "There can be up to two different edge textures for a block.")
        self.defineLabel(self.frame, "One for the upper side of the block, and another for the down side of the block.")
        self.defineLabel(self.frame, "")
        self.defineLabel(self.frame, "The edge drawing behaviour:")
        buttons = [('using the given angle', 'angle'), ('inside the block', 'in'), ('outside the block', 'out')]
        self.drawMethod = self.defineRadioButtons(self.frame, getValue(self.commonValues, 'edges', 'drawmethod', default='angle'),
                                                  buttons, command=self.edgeDrawCallback)

        self.edgeFrame = Tkinter.Frame(self.frame)
        defaultEdge    = getValue(self.commonValues, 'edge', 'texture', default='_None_')
        self.defineLabel(self.edgeFrame, "Upper edge texture", grid=(0, 0))
        self.upperEdge = XmotoBitmap(self.edgeFrame, edgeTextures[defaultEdge], defaultEdge, self.edgeSelectionWindow, grid=(0, 1), buttonName='upperEdge')

        defaultDownEdge= getValue(self.commonValues, 'edge', 'downtexture', default='_None_')
        self.downEdgeLabel = XmotoLabel(self.edgeFrame, "Down edge texture", grid=(1, 0))
        self.downEdge      = XmotoBitmap(self.edgeFrame, edgeTextures[defaultDownEdge], defaultDownEdge, self.edgeSelectionWindow, grid=(1, 1), buttonName='downEdge')
        self.edgeFrame.pack()

        self.angleLabel = self.defineLabel(self.frame, "The angle the edges point to (defaulted to 270.0):")
        self.angle = XmotoScale(self.frame, getValue(self.commonValues, 'edges', 'angle', default=self.defaultAngle), label='Edge angle', from_=0, to=360, resolution=45, default=self.defaultAngle)

        # physic
        self.defineTitle(self.frame, "Physic")
        self.defineLabel(self.frame, "The bigger the value, the bigger the grip.")
        self.defineLabel(self.frame, "Default value in Xmoto is 20.0")
        self.grip = XmotoEntry(self.frame, getValue(self.commonValues, 'physics', 'grip', default=self.defaultGrip), label='Block grip')

        self.defineOkCancelButtons(self.frame, command=self.okPressed)

        # to update disabled buttons
        self.edgeDrawCallback()

        self.root.mainloop()

    def edgeDrawCallback(self):
        if self.drawMethod.get() in ['angle']:
            self.angle.show()
            self.downEdgeLabel.show()
            self.downEdge.show()
        elif self.drawMethod.get() in ['in', 'out']:
            self.angle.hide()
            self.downEdgeLabel.hide()
            self.downEdge.hide()

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        if buttonName in ['texture']:
            bitmapDict = textures
        elif buttonName in ['downEdge', 'upperEdge']:
            bitmapDict = edgeTextures

        values = self.__dict__[buttonName].update(imgName, bitmapDict)

e = ChangeBlock()
e.affect()
