from xmotoExtension import XmotoExtension
from parsers import LabelParser
from svgnode import setNodeAsCircle
from inksmoto_configuration import defaultCollisionRadius, svg2lvlRatio
from xmotoTools import getValue
from inkex import addNS

class AddEntity(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        changes = []

        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == self.typeid):
            self.label.clear()

        changes.append(['typeid', self.typeid])

        return changes

    def updateNodeSvgAttributes(self, node):
        node.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())
        node.set('style', self.getStyleValue())

        typeid = self.typeid
        if typeid == 'EndOfLevel':
            typeid = 'Flower'

        (descriptionNode, metadata) = self.getMetaData()
        metadata = LabelParser().parse(metadata)
        levelScale = float(getValue(metadata, 'remplacement', typeid+'Scale', 1.0))
        
        setNodeAsCircle(node, levelScale * defaultCollisionRadius[self.typeid] / svg2lvlRatio)
