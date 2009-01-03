from xmotoExtension import XmotoExtension
from svgnode import setNodeAsRectangle
from inkex import addNS

class AddZone(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        changes = []

        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == 'Zone'):
            self.label.clear()

        changes.append(['typeid', 'Zone'])

        return changes

    def updateNodeSvgAttributes(self, node):
        node.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())
        node.set('style', self.getStyleValue())

        setNodeAsRectangle(node)

if __name__ == "__main__":
    e = AddZone()
    e.affect()
