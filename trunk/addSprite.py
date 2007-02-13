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
        
        

    def getLabelChanges(self):
        changes = []

        # previously not a sprite
        if not (self.label.has_key('typeid') and self.label['typeid'] == 'Sprite'):
            self.label.clear()

        changes.append(['typeid', 'Sprite'])
        if self.options.updatesprite == 'true':
          changes.append(['param', {'name': self.options.name}])

        if self.options.update == 'true':
          changes.append(['param', {'z':    self.options.z}])
          changes.append(['position', {'angle': deg2rad(self.options.angle),
                                       'reversed': self.options.reversed
                                       }])

        return changes

e = AddSprite()
e.affect()
