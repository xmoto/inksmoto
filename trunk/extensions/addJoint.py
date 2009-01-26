from xmotoExtension import XmExt
from inkex import addNS
from svgnode import createNewNode, getNodeAABB, getJointPath
from xmotoTools import createIfAbsent
import log

class AddJoint(XmExt):
    def __init__(self, jointType):
        XmExt.__init__(self)
        self.jointType = jointType

    def effectHook(self):
        """ we need to manipulate the two selected items """
        if len(self.selected) != 2:
            msg = "You have to select the two objects to join together."
            log.outMsg(msg)
            return False

        # check that the objects are paths or rectangles
        for node in self.selected.values():
            if node.tag not in [addNS('path', 'svg'), addNS('rect', 'svg')]:
                msg = "You need to select path and rectangle only."
                log.outMsg(msg)
                return False
            self.parseLabel(node.get(addNS('xmoto_label', 'xmoto'), ''))
            createIfAbsent(self.label, 'position')
            if 'physics' not in self.label['position']:
                msg = "The selected objects has to be Xmoto physics blocks."
                log.outMsg(msg)
                return False

        block1Id = self.options.ids[0]
        block2Id = self.options.ids[1]

        anchorId = block1Id + block2Id + '_joint_' + self.jointType
        parentNode = self.selected[block1Id].getparent()
        anchorNode = self.createJointNode(parentNode, anchorId,
                                          self.selected[block1Id],
                                          self.selected[block2Id])

        self.setLabelAndStyle(block1Id, block2Id)
        self.updateNodeSvgAttributes(anchorNode)

        return False

    def createJointNode(self, parent, jid, block1, block2):
        aabb1 = getNodeAABB(block1)
        aabb1.applyTransform(block1.get('transform', ''))
        aabb2 = getNodeAABB(block2)
        aabb2.applyTransform(block2.get('transform', ''))

        tag = addNS('path', 'svg')
        node = createNewNode(parent, jid, tag)
        node.set('d', getJointPath(self.jointType, aabb1, aabb2))

        return node

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
