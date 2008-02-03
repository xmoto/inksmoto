from xmotoExtension import XmotoExtension
from listAvailableElements import sprites
import math

def deg2rad(angle):
  return angle*(math.pi/180.0)

class AddSprite(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--name", type="string", dest="name", 
                                     help="sprite name")
        self.OptionParser.add_option("--z", type="int", dest="z", 
                                     help="sprite z")
        self.OptionParser.add_option("--angle", type="float", dest="angle",
                                     help="rotation angle in degrees")
        self.OptionParser.add_option("--reversed", type="string", dest="reversed",
                                     help="x axis reverse")
        self.OptionParser.add_option("--update", type="string",
                                     dest="update", help="if true, update the sprite properties")
        self.OptionParser.add_option("--updatesprite", type="string",
                                     dest="updatesprite", help="if true, update the sprite texture")
        self.OptionParser.add_option("--r",  type="float", dest="radius",  help="sprite collision radius")
        self.OptionParser.add_option("--width",  type="float", dest="width",  help="sprite width")
        self.OptionParser.add_option("--height", type="float", dest="height", help="sprite height")
        self.OptionParser.add_option("--updatedims", type="string", dest="updatedims", help="if true, update the sprite dimensions")
        
        

    def getLabelChanges(self):
        changes = []

        # previously not a sprite
        if not (self.label.has_key('typeid') and self.label['typeid'] == 'Sprite'):
            self.label.clear()

        changes.append(['typeid', 'Sprite'])
        if self.options.updatesprite == 'true':
          changes.append(['param', {'name': self.options.name}])

        if self.options.updatedims == 'true':
          changes.append(['size', {'r':self.options.radius, 'width':self.options.width, 'height':self.options.height}])

        if self.options.update == 'true':
          changes.append(['param', {'z':    self.options.z}])
          changes.append(['position', {'angle': deg2rad(self.options.angle),
                                       'reversed': self.options.reversed
                                       }])

        return changes

e = AddSprite()
e.affect()
