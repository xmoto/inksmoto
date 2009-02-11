from inksmoto.xmotoExtensionTkinter import XmExtTkElement
from inksmoto.xmotoTools import createIfAbsent, delWithoutExcept, NOTSET_BITMAP
from inksmoto.listAvailableElements import TEXTURES, EDGETEXTURES
from inksmoto import xmGui
from inksmoto.factory import Factory

class ChangeBlock(XmExtTkElement):
    def __init__(self):
        XmExtTkElement.__init__(self)
        self.defScale = 1.0
        self.defAngle = 270.0
        self.defMethod = 'angle'
        self.namespacesInCommon = ['usetexture', 'edge', 'edges']

    def getUserChanges(self):
        delWithoutExcept(self.commonValues, 'usetexture')
        delWithoutExcept(self.commonValues, 'edge')
        delWithoutExcept(self.commonValues, 'edges')
        # if the block has been set as an entity
        delWithoutExcept(self.commonValues, 'typeid')

        # handle texture
        createIfAbsent(self.commonValues, 'usetexture')

        if self.texture.get() in NOTSET_BITMAP:
            raise Exception('You have to give a texture to the block')

        self.defaultValues.setOrDelBitmap(self.commonValues, 'usetexture', 'id', self.texture)
        if self.scale.get() != self.defScale:
            self.commonValues['usetexture']['scale'] = self.scale.get()

        # handle edges
        createIfAbsent(self.commonValues, 'edge')
        createIfAbsent(self.commonValues, 'edges')

        if self.drawMethod.get() != self.defMethod:
            self.commonValues['edges']['drawmethod'] = self.drawMethod.get()
        if self.drawMethod.get() in ['angle']:
            if self.angle.get() != self.defAngle:
                self.commonValues['edges']['angle'] = self.angle.get()

            self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                              'texture',     self.upperEdge)
            self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                              'downtexture', self.downEdge)

            # no edge texture selected
            if ('texture' not in self.commonValues['edge']
                and 'downtexture' not in self.commonValues['edge']):
                delWithoutExcept(self.commonValues, 'edge')
                delWithoutExcept(self.commonValues, 'edges')

        elif self.drawMethod.get() in ['in', 'out']:
            delWithoutExcept(self.commonValues['edges'], 'angle')
            delWithoutExcept(self.commonValues['edge'],  'downtexture')
            self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                              'texture', self.upperEdge)

            # no edge texture selected
            if 'texture' not in self.commonValues['edge']:
                delWithoutExcept(self.commonValues, 'edge')
                delWithoutExcept(self.commonValues, 'edges')

        return self.commonValues

    def createWindow(self):
        f = Factory()
        xmGui.defineWindowHeader(title='Block textures')

        # texture
        f.createObject('XmTitle', "Texture")
        f.createObject('XmLabel', "Click the texture to choose another one.")
        defaultTexture = self.defaultValues.get(self.commonValues, 'usetexture',
                                                'id', default='_None_')
        self.texture = f.createObject('XmBitmap',
                                      TEXTURES[defaultTexture]['file'],
                                      defaultTexture,
                                      toDisplay='textures',
                                      callback=self.updateBitmap,
                                      buttonName='texture')
        value = self.defaultValues.get(self.commonValues, 'usetexture', 'scale',
                                       default=self.defScale)
        self.scale = f.createObject('XmScale',
                                    value,
                                    label='Scale', from_=0.1, to=10,
                                    resolution=0.1, default=self.defScale)

        # edges
        f.createObject('XmTitle', "Edge")
        f.createObject('XmLabel', "Edge drawing behaviour:")
        buttons = [('using the given angle', 'angle'),
                   ('inside the block', 'in'),
                   ('outside the block', 'out')]
        value = self.defaultValues.get(self.commonValues, 'edges',
                                       'drawmethod', default='angle')
        self.drawMethod = f.createObject('XmRadio', value,
                                         buttons, command=self.edgeDrawCallback)

        xmGui.newFrame()
        defaultEdge = self.defaultValues.get(self.commonValues, 'edge',
                                             'texture', default='_None_')
        f.createObject('XmLabel', "Upper edge texture", grid=(0, 0))
        self.upperEdge = f.createObject('XmBitmap',
                                        EDGETEXTURES[defaultEdge]['file'],
                                        defaultEdge,
                                        toDisplay='edges',
                                        callback=self.updateBitmap,
                                        grid=(0, 1), buttonName='upperEdge')

        defaultDownEdge = self.defaultValues.get(self.commonValues, 'edge',
                                                 'downtexture', default='_None_')
        self.downEdgeLabel = f.createObject('XmLabel',
                                            "Down edge texture",
                                            grid=(1, 0))
        self.downEdge = f.createObject('XmBitmap',
                                       EDGETEXTURES[defaultDownEdge]['file'],
                                       defaultDownEdge,
                                       toDisplay='edges',
                                       callback=self.updateBitmap,
                                       grid=(1, 1), buttonName='downEdge')
        xmGui.popFrame()

        label = "Angle the edges point to (defaulted to 270.0):"
        self.angleLabel = f.createObject('XmLabel', label)
        value = self.defaultValues.get(self.commonValues, 'edges',
                                       'angle', default=self.defAngle)
        self.angle = f.createObject('XmScale',
                                    value,
                                    label='Edge angle', from_=0, to=360,
                                    resolution=45, default=self.defAngle)

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

    def updateBitmap(self, imgName, buttonName):
        if buttonName in ['texture']:
            bitmapDict = TEXTURES
        elif buttonName in ['downEdge', 'upperEdge']:
            bitmapDict = EDGETEXTURES

        self.__dict__[buttonName].update(imgName, bitmapDict)

def run():
    e = ChangeBlock()
    e.affect()
    return e

if __name__ == "__main__":
    run()
