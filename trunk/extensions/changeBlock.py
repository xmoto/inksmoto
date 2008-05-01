from xmotoExtensionTkinter import XmotoExtTkElement, XmotoListbox, XmotoScale, XmotoEntry, XmotoBitmap, XmotoLabel
from xmotoTools import getValue, createIfAbsent, delWithoutExcept, notSetBitmap, setOrDelBool, setOrDelBitmap
from listAvailableElements import textures, edgeTextures
import Tkinter

class ChangeBlock(XmotoExtTkElement):
    def __init__(self):
        XmotoExtTkElement.__init__(self)
        self.defaultGrip  = 20.0
        self.defaultAngle = 270.0
        self.defaultMass  = 30.0
        self.defaultElasticity = 0.0
        self.defaultFriction = 0.5

    def getUserChanges(self):
        self.commonValues = {}

        # handle texture
        createIfAbsent(self.commonValues, 'usetexture')

        if self.texture.get() in notSetBitmap:
            raise Exception('You have to give a texture to the block')

        setOrDelBitmap(self.commonValues['usetexture'], 'id', self.texture)

        # handle position
        createIfAbsent(self.commonValues, 'position')
        setOrDelBool(self.commonValues['position'], self.background, 'background')
        setOrDelBool(self.commonValues['position'], self.dynamic,    'dynamic')
        setOrDelBool(self.commonValues['position'], self.physics,    'physics')

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

        createIfAbsent(self.commonValues, 'physics')
        self.commonValues['physics']['grip'] = self.grip.get()
        if 'physics' in self.commonValues['position']:
            self.commonValues['physics']['mass']       = self.mass.get()
            self.commonValues['physics']['elasticity'] = self.elasticity.get()
            self.commonValues['physics']['friction']   = self.friction.get()
        else:
            for var in ['mass', 'elasticity', 'friction']:
                delWithoutExcept(self.commonValues['physics'], var)

        return self.commonValues

    def createWindow(self):
        self.defineWindowHeader(title='Block properties')

        # texture
        self.defineTitle(self.frame, "Texture")
        self.defineLabel(self.frame, "Click the texture to choose another one.")
        defaultTexture  = getValue(self.commonValues, 'usetexture', 'id', default='_None_')
        self.texture = XmotoBitmap(self.frame, textures[defaultTexture], defaultTexture, self.textureSelectionWindow, buttonName='texture')

        # type
        self.defineTitle(self.frame, "Type")
        #self.defineLabel(self.frame, "Uncheck both to convert into normal block.")
        self.background = self.defineCheckbox(self.frame, getValue(self.commonValues, 'position', 'background'), text='Background block')
        self.dynamic    = self.defineCheckbox(self.frame, getValue(self.commonValues, 'position', 'dynamic'),    text='Dynamic block')
        self.physics    = self.defineCheckbox(self.frame, getValue(self.commonValues, 'position', 'physics'),    text='Physics block', command=self.physicsCallback)

        # edges
        self.defineTitle(self.frame, "Edge")
        self.defineLabel(self.frame, "Edge drawing behaviour:")
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

        #self.angleLabel = self.defineLabel(self.frame, "Angle the edges point to (defaulted to 270.0):")
        self.angle = XmotoScale(self.frame, getValue(self.commonValues, 'edges', 'angle', default=self.defaultAngle), label='Edge angle', from_=0, to=360, resolution=45, default=self.defaultAngle)

        # physic
        self.defineTitle(self.frame, "Physic")
        self.grip = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'grip', default=self.defaultGrip), label='Grip', from_=0, to=50, resolution=1, default=self.defaultGrip)
        self.mass = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'mass', default=self.defaultMass), label='Mass', from_=1, to=500, resolution=1, default=self.defaultMass)
        self.elasticity = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'elasticity', default=self.defaultElasticity), label='Elasticity', from_=0.0, to=1.0, resolution=0.1, default=self.defaultElasticity)
        self.friction = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'friction', default=self.defaultFriction), label='Friction', from_=0.0, to=1.0, resolution=0.1, default=self.defaultFriction)
        self.physicsCallback()

        # to update disabled buttons
        self.edgeDrawCallback()

    def physicsCallback(self):
        if self.physics.get() == 1:
            self.mass.show()
            self.elasticity.show()
            self.friction.show()
        else:
            self.mass.hide()
            self.elasticity.hide()
            self.friction.hide()

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
