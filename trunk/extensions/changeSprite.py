from inksmoto.xmotoExtensionTkinter import XmExtTkElement
from inksmoto.xmotoTools import createIfAbsent
from inksmoto.availableElements import AvailableElements
from math import radians, degrees
from inksmoto import xmGui
from inksmoto.factory import Factory

class ChangeSprite(XmExtTkElement):
    def __init__(self):
        XmExtTkElement.__init__(self)
        self.defaultZ = -1
        self.defaultAngle = 0
        self.defaultScale = 1

    def getUserChanges(self):
        self.commonValues = {}
        self.commonValues['typeid'] = 'Sprite'

        createIfAbsent(self.commonValues, 'param')
        self.defaultValues.setOrDelBitmap(self.commonValues, 'param', 'name', self.sprite)

        if 'name' not in self.commonValues['param']:
            raise Exception("You have to set the sprite bitmap")

        self.commonValues['param']['z'] = self.z.get()

        createIfAbsent(self.commonValues, 'position')
        self.commonValues['position']['angle'] =  radians(self.angle.get())
        self.defaultValues.setOrDelBool(self.commonValues, 'position',
                                        self.reversed, 'reversed')

        createIfAbsent(self.commonValues, 'size')
        self.commonValues['size']['scale'] = self.scale.get()

        return self.commonValues

    def createWindow(self):
        f = Factory()
        xmGui.defineWindowHeader(title='Sprite properties')

        f.createObject('XmTitle', "Sprite")

        defaultSprite = self.defaultValues.get(self.commonValues, 'param',
                                               'name', default='_None_')
        f.createObject('XmLabel', 'Sprite image:')
        self.sprite = f.createObject('XmBitmap',
                                     'self.sprite',
                                     AvailableElements()['SPRITES'][defaultSprite]['file'],
                                     defaultSprite,
                                     toDisplay='sprites',
                                     callback=self.updateBitmap,
                                     buttonName='sprite')

        f.createObject('XmTitle', "Properties")
        value = self.defaultValues.get(self.commonValues, 'param',
                                       'z', default=self.defaultZ)
        self.z = f.createObject('XmScale',
                                'self.z', value,
                                label='Sprite z:', from_=-1, to=1,
                                resolution=1, default=self.defaultZ)
        angle = self.defaultValues.get(self.commonValues, 'position',
                                       'angle', default=self.defaultAngle)
        self.angle = f.createObject('XmScale',
                                    'self.angle',
                                    degrees(float(angle)),
                                    label='Rotation angle:', from_=0, to=360,
                                    resolution=45, default=self.defaultAngle)
        value = self.defaultValues.get(self.commonValues, 'position', 'reversed')
        self.reversed = f.createObject('XmCheckbox',
                                       'self.reversed', value,
                                       text='Reverse the sprite (x-axis):')

        f.createObject('XmTitle', "Dimensions")
        value = self.defaultValues.get(self.commonValues, 'size',
                                       'scale', default=self.defaultScale)
        self.scale = f.createObject('XmScale',
                                    'self.scale', value,
                                    label='Sprite scale:', from_=0.1, to=10,
                                    resolution=0.1, default=self.defaultScale)

    def updateBitmap(self, imgName, buttonName):
        self.sprite.update(imgName, AvailableElements()['SPRITES'])

def run():
    ext = ChangeSprite()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
