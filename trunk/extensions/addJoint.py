from xmotoExtension import XmotoExtension
from inkex import addNS
from svgnode import newNode, getNodeAABB, getCenteredCircleSvgPath
from xmotoTools import createIfAbsent
from inksmoto_configuration import defaultCollisionRadius, svg2lvlRatio
import log

class AddJoint(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def effectHook(self):
        """ we need to manipulate the two selected items """
        if len(self.selected) != 2:
            log.writeMessageToUser("You have to select the two objects to join together.")
            return

        # check that the objects are paths or rectangles
        for (id, node) in self.selected.iteritems():
            if node.tag not in [addNS('path', 'svg'), addNS('rect', 'svg')]:
                log.writeMessageToUser("You need to select path and rectangle only.")
                return
            self.parseLabel(node.get(addNS('xmoto_label', 'xmoto'), ''))
            createIfAbsent(self.label, 'position')
            if 'physics' not in self.label['position']:
                log.writeMessageToUser("The selected object has to be an Xmoto physical block.")
                return

        block1Id = self.options.ids[0]
        block2Id = self.options.ids[1]

        anchorId = block1Id + block2Id + '_joint_' + self.jointType
        parentNode = self.selected[block1Id].xpath('..')[0]
        anchorNode = self.createJointNode(parentNode, anchorId, self.selected[block1Id], self.selected[block2Id])

        self.setLabelAndStyle(block1Id, block2Id)
        self.updateNodeSvgAttributes(anchorNode)

        return False

    def createJointNode(self, parent, id, block1, block2):
        aabb1 = getNodeAABB(block1)
        aabb2 = getNodeAABB(block2)

        tag = addNS('path', 'svg')
        node = newNode(parent, id, tag)
        node.set('d', self.getJointPath(self.jointType, aabb1, aabb2))

        return node

    def getJointPath(self, jointType, aabb1, aabb2):
        radius = defaultCollisionRadius['Joint'] / svg2lvlRatio

        if jointType == 'pivot':
            cx = (aabb1.cx() + aabb2.cx()) / 2.0
            cy = (aabb1.cy() + aabb2.cy()) / 2.0
            return getCenteredCircleSvgPath(cx, cy, radius)
        elif jointType == 'pin':
            w = abs(aabb1.cx() - aabb2.cx())
            h = abs(aabb1.cy() - aabb2.cy())
            if w > h:
                d = 'M %f,%f L %f,%f L %f,%f L %f,%f L %f,%f z' % (aabb1.cx(), aabb1.cy()+radius/2.0,
                                                                   aabb2.cx(), aabb2.cy()+radius/2.0,
                                                                   aabb2.cx(), aabb2.cy()-radius/2.0,
                                                                   aabb1.cx(), aabb1.cy()-radius/2.0,
                                                                   aabb1.cx(), aabb1.cy()+radius/2.0)
            else:
                d = 'M %f,%f L %f,%f L %f,%f L %f,%f L %f,%f z' % (aabb1.cx()-radius/2.0, aabb1.cy(),
                                                                   aabb2.cx()-radius/2.0, aabb2.cy(),
                                                                   aabb2.cx()+radius/2.0, aabb2.cy(),
                                                                   aabb1.cx()+radius/2.0, aabb1.cy(),
                                                                   aabb1.cx()-radius/2.0, aabb1.cy())
            return d

    def setLabelAndStyle(self, block1Id, block2Id):
        self.label = {'typeid':'Joint',
                      'joint':
                      {'type':'%s' % self.jointType,
                       'connection-start':block1Id,
                       'connection-end':block2Id
                      }
                     }

        self.unparseLabel()
        self.generateStyle()
        self.unparseStyle()
