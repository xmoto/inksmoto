from xmotoExtensionTkinter import XmotoExtTkElement, XmBitmap, XmScale
from xmotoExtensionTkinter import XmCheckbox, XmLabel, XmTitle
from xmotoTools import createIfAbsent
from listAvailableElements import SPRITES
from math import radians, degrees

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

        if 'name' not in self.commonValues['param']:
            raise Exception("You have to set the sprite bitmap")

        self.commonValues['param']['z'] = self.z.get()

        createIfAbsent(self.commonValues, 'position')
        self.commonValues['position']['angle'] =  radians(self.angle.get())
        self.setOrDelBool(self.commonValues, 'position',
                          self.reversed, 'reversed')

        createIfAbsent(self.commonValues, 'size')
        self.commonValues['size']['scale'] = self.scale.get()

        return self.commonValues

    def createWindow(self):
        self.defineWindowHeader(title='Sprite properties')

        XmTitle(self.frame, "Sprite")

        defaultSprite = self.getValue(self.commonValues, 'param',
                                      'name', default='_None_')
        XmLabel(self.frame, 'Sprite image:')
        self.sprite = XmBitmap(self.frame,
                               SPRITES[defaultSprite]['file'],
                               defaultSprite,
                               self.spriteSelectionWindow,
                               buttonName='sprite')

        XmTitle(self.frame, "Properties")
        self.z = XmScale(self.frame,
                         self.getValue(self.commonValues, 'param',
                                       'z', default=self.defaultZ),
                         label='Sprite z:', from_=-1, to=1,
                         resolution=1, default=self.defaultZ)
        angle = self.getValue(self.commonValues, 'position',
                              'angle', default=self.defaultAngle)
        self.angle = XmScale(self.frame,
                             degrees(float(angle)),
                             label='Rotation angle:', from_=0, to=360,
                             resolution=45, default=self.defaultAngle)
        self.reversed = XmCheckbox(self.frame,
                                   self.getValue(self.commonValues,
                                                 'position',
                                                 'reversed'),
                                   text='Reverse the sprite (x-axis):')

        XmTitle(self.frame, "Dimensions")
        self.scale = XmScale(self.frame,
                             self.getValue(self.commonValues, 'size',
                                           'scale', default=self.defaultScale),
                             label='Sprite scale:', from_=0.1, to=10,
                             resolution=0.1, default=self.defaultScale)

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.sprite.update(imgName, SPRITES)

def run():
    ext = ChangeSprite()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
