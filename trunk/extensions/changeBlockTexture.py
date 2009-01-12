from xmotoExtensionTkinter import XmotoExtTkElement, XmotoListbox, XmotoScale, XmotoEntry, XmotoBitmap, XmotoLabel
from xmotoTools import createIfAbsent, delWithoutExcept, notSetBitmap, setOrDelBool, setOrDelBitmap
from listAvailableElements import textures, edgeTextures
import Tkinter

class ChangeBlock(XmotoExtTkElement):
    def __init__(self):
        XmotoExtTkElement.__init__(self)
        self.defaultScale = 1.0
        self.defaultAngle = 270.0
        self.namespacesInCommon = ['usetexture', 'edge', 'edges']

    def getUserChanges(self):
        delWithoutExcept(self.commonValues, 'usetexture')
        delWithoutExcept(self.commonValues, 'edge')
        delWithoutExcept(self.commonValues, 'edges')
        # if the block has been set as an entity
        delWithoutExcept(self.commonValues, 'typeid')

        # handle texture
        createIfAbsent(self.commonValues, 'usetexture')

        if self.texture.get() in notSetBitmap:
            raise Exception('You have to give a texture to the block')

        setOrDelBitmap(self.commonValues['usetexture'], 'id', self.texture)
        self.commonValues['usetexture']['scale'] = self.scale.get()

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

    def createWindow(self):
        self.defineWindowHeader(title='Block textures')

        # texture
        self.defineTitle(self.frame, "Texture")
        self.defineLabel(self.frame, "Click the texture to choose another one.")
        defaultTexture  = self.getValue(self.commonValues, 'usetexture', 'id', default='_None_')
        self.texture = XmotoBitmap(self.frame, textures[defaultTexture]['file'], defaultTexture, self.textureSelectionWindow, buttonName='texture')
        self.scale = XmotoScale(self.frame, self.getValue(self.commonValues, 'usetexture', 'scale', default=self.defaultScale), label='Scale', from_=0.1, to=10, resolution=0.1, default=self.defaultScale)

        # edges
        self.defineTitle(self.frame, "Edge")
        self.defineLabel(self.frame, "Edge drawing behaviour:")
        buttons = [('using the given angle', 'angle'), ('inside the block', 'in'), ('outside the block', 'out')]
        self.drawMethod = self.defineRadioButtons(self.frame, self.getValue(self.commonValues, 'edges', 'drawmethod', default='angle'),
                                                  buttons, command=self.edgeDrawCallback)

        self.edgeFrame = Tkinter.Frame(self.frame)
        defaultEdge    = self.getValue(self.commonValues, 'edge', 'texture', default='_None_')
        self.defineLabel(self.edgeFrame, "Upper edge texture", grid=(0, 0))
        self.upperEdge = XmotoBitmap(self.edgeFrame, edgeTextures[defaultEdge]['file'], defaultEdge, self.edgeSelectionWindow, grid=(0, 1), buttonName='upperEdge')

        defaultDownEdge= self.getValue(self.commonValues, 'edge', 'downtexture', default='_None_')
        self.downEdgeLabel = XmotoLabel(self.edgeFrame, "Down edge texture", grid=(1, 0))
        self.downEdge      = XmotoBitmap(self.edgeFrame, edgeTextures[defaultDownEdge]['file'], defaultDownEdge, self.edgeSelectionWindow, grid=(1, 1), buttonName='downEdge')
        self.edgeFrame.pack()

        self.angleLabel = self.defineLabel(self.frame, "Angle the edges point to (defaulted to 270.0):")
        self.angle = XmotoScale(self.frame, self.getValue(self.commonValues, 'edges', 'angle', default=self.defaultAngle), label='Edge angle', from_=0, to=360, resolution=45, default=self.defaultAngle)

        # to update disabled buttons
        self.edgeDrawCallback()

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

if __name__ == "__main__":
    e = ChangeBlock()
    e.affect()
