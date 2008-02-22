from xmotoExtensionTkinter import XmotoExtTkElement, XmotoBitmap, XmotoScale
from xmotoTools import getValue, createIfAbsent, setOrDelBool, setOrDelBitmap
from listAvailableElements import sprites
import logging, log

class ChangeSprite(XmotoExtTkElement):
    def __init__(self):
        XmotoExtTkElement.__init__(self)
        self.defaultZ = -1
        self.defaultAngle = 0
        self.defaultRadius = 0.5

    def getUserChanges(self):
        self.commonValues['typeid'] = 'Sprite'

        createIfAbsent(self.commonValues, 'param')
        setOrDelBitmap(self.commonValues['param'], 'name', self.sprite)
        
        createIfAbsent(self.commonValues, 'position')
        self.commonValues['position']['angle'] =  self.angle.get()
        setOrDelBool(self.commonValues['position'], self.reversed, 'reversed')

        createIfAbsent(self.commonValues, 'size')
        self.commonValues['size']['z'] = self.z.get()
        radiusValue = self.radius.get()
        self.commonValues['size']['r'] = radiusValue
        #self.commonValues['size']['width']  = radiusValue * 2
        #self.commonValues['size']['height'] = radiusValue * 2

        return self.commonValues

    def createWindow(self):
        self.defineWindowHeader(title='Sprite properties')

        self.defineTitle(self.frame, "Sprite")

        logging.info(str(self.commonValues))

        defaultSprite = getValue(self.commonValues, 'param', 'name', default='_None_')
        self.defineLabel(self.frame, 'Sprite image:')
        self.sprite = XmotoBitmap(self.frame, sprites[defaultSprite], defaultSprite, self.spriteSelectionWindow, buttonName='sprite')

        self.defineTitle(self.frame, "Properties")
        self.z = XmotoScale(self.frame, getValue(self.commonValues, 'size', 'z', default=self.defaultZ), label='Sprite z:', from_=-1, to=1, resolution=1, default=self.defaultZ)
        self.angle = XmotoScale(self.frame, getValue(self.commonValues, 'position', 'angle', default=self.defaultAngle), label='Rotation angle:', from_=0, to=360, resolution=45, default=self.defaultAngle)
        self.reversed = self.defineCheckbox(self.frame, getValue(self.commonValues, 'position', 'reversed'), label='Reverse the sprite (x-axis):')
        

        self.defineTitle(self.frame, "Dimensions")
        self.radius = XmotoScale(self.frame, getValue(self.commonValues, 'size', 'r', default=self.defaultRadius), label='Sprite collision radius:', from_=0.1, to=5.0, resolution=0.1, default=self.defaultRadius)

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.sprite.update(imgName, sprites)

e = ChangeSprite()
e.affect()
