from xmotoExtension import XmotoExtension

class AddEntity(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--updatedims", type="string", dest="updatedims", help="if true, update the sprite dimensions")        
        self.OptionParser.add_option("--r",  type="float", dest="radius",  help="sprite collision radius")
        self.OptionParser.add_option("--width",  type="float", dest="width",  help="sprite width")
        self.OptionParser.add_option("--height", type="float", dest="height", help="sprite height")

    def getLabelChanges(self):
        changes = []

        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == self.typeid):
            self.label.clear()

        changes.append(['typeid', self.typeid])

        if self.options.updatedims == 'true':
          changes.append(['size', {'r':self.options.radius, 'width':self.options.width, 'height':self.options.height}])

        return changes
