from xmotoExtensionTkinter import XmotoExtTkElement, XmotoBitmap, XmotoScale, XmotoCheckBox
from xmotoTools import createIfAbsent
from listAvailableElements import sprites
from svgnode import setNodeAsCircle
from inkex import addNS
from inksmoto_configuration import defaultCollisionRadius, svg2lvlRatio
from math import radians, degrees
import logging, log

class ChangeSprite(XmotoExtTkElement):
    def __init__(self):
        XmotoExtTkElement.__init__(self)
        self.defaultZ = -1
        self.defaultAngle = 0
        self.defaultScale = 1

    def getUserChanges(self):
        self.commonValues = {}
        self.commonValues['typeid'] = 'Sprite'

        createIfAbsent(self.commonValues, 'param')
        self.setOrDelBitmap(self.commonValues, 'param', 'name', self.sprite)

        try:
            self.commonValues['param']['name']
        except:
            raise Exception("You have to set the sprite bitmap")

        self.commonValues['param']['z'] = self.z.get()

        createIfAbsent(self.commonValues, 'position')
        self.commonValues['position']['angle'] =  radians(self.angle.get())
        self.setOrDelBool(self.commonValues, 'position', self.reversed, 'reversed')

        createIfAbsent(self.commonValues, 'size')
        self.commonValues['size']['scale'] = self.scale.get()

        return self.commonValues

    def createWindow(self):
        self.defineWindowHeader(title='Sprite properties')

        self.defineTitle(self.frame, "Sprite")

        defaultSprite = self.getValue(self.commonValues, 'param', 'name', default='_None_')
        self.defineLabel(self.frame, 'Sprite image:')
        self.sprite = XmotoBitmap(self.frame, sprites[defaultSprite]['file'], defaultSprite, self.spriteSelectionWindow, buttonName='sprite')

        self.defineTitle(self.frame, "Properties")
        self.z = XmotoScale(self.frame, self.getValue(self.commonValues, 'param', 'z', default=self.defaultZ), label='Sprite z:', from_=-1, to=1, resolution=1, default=self.defaultZ)
        self.angle = XmotoScale(self.frame, degrees(float(self.getValue(self.commonValues, 'position', 'angle', default=self.defaultAngle))), label='Rotation angle:', from_=0, to=360, resolution=45, default=self.defaultAngle)
        self.reversed = XmotoCheckBox(self.frame, self.getValue(self.commonValues, 'position', 'reversed'), text='Reverse the sprite (x-axis):')

        self.defineTitle(self.frame, "Dimensions")
        self.scale = XmotoScale(self.frame, self.getValue(self.commonValues, 'size', 'scale', default=self.defaultScale), label='Sprite scale:', from_=0.1, to=10, resolution=0.1, default=self.defaultScale)

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.sprite.update(imgName, sprites)

if __name__ == "__main__":
    e = ChangeSprite()
    e.affect()
