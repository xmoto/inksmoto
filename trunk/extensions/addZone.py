from xmotoExtension import XmotoExtension
from svgnode import setNodeAsRectangle
from inkex import addNS

class AddZone(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == 'Zone'):
            self.label.clear()

        return {'typeid': 'Zone'}

if __name__ == "__main__":
    e = AddZone()
    e.affect()
