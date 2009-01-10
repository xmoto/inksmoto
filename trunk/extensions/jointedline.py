from inkex import addNS
from xmotoExtension import XmotoExtension
from xmotoTools import createIfAbsent
from aabb import AABB
from addPinJoint import AddPinJoint
from addPivotJoint import AddPivotJoint
from svgnode import getCenteredCircleSvgPath
from lxml import etree
import svgnode
import logging, log

class JointedLine(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

        self.OptionParser.add_option("-s", "--space",  type="float",  dest="space",  help="space between blocks")
        self.OptionParser.add_option("-j", "--joint",  type="string", dest="joint",  help="type of joint")
        self.OptionParser.add_option("-b", "--blocks", type="int",    dest="blocks", help="number of blocks in the line")

    def effectHook(self):
        #read svg information, find selected path to use in the line.
        if len(self.selected) != 1:
	    log.writeMessageToUser("You have to select only one object.")
	    return False

        for (id, node) in self.selected.iteritems():
            if node.tag not in [addNS('path', 'svg'), addNS('rect', 'svg')]:
                log.writeMessageToUser("You need to select path and rectangle only.")
                return False

        # there's only one selected object
        node = self.selected.values()[0]

        self.jointType = self.options.joint
        self.space     = self.options.space
        self.numBlocks = self.options.blocks

        # is it a physic block?
        self.parseLabel(node.get(addNS('xmoto_label', 'xmoto'), ''))
        createIfAbsent(self.label, 'position')
        if 'physics' not in self.label['position']:
            log.writeMessageToUser("The selected object has to be an Xmoto physics block.")
            return False

        # we need uniq ids
        idPrefix = node.get('id')
        blockPrefix = idPrefix + 'jl_block'
        jointPrefix = idPrefix + 'jl_joint'

        node.set('id', blockPrefix + '0')

        aabb = svgnode.getNodeAABB(node)
        offset = self.space + aabb.width()
        jointHeight = 10

        for no in xrange(1, self.numBlocks+1):
            newNode = svgnode.duplicateNode(node, blockPrefix+str(no))
            svgnode.translateNode(newNode, offset, 0)

            if no < self.numBlocks+1:
                node = newNode

                newJoint = None
                ex = None
                if self.jointType == 'pin':
                    ex = AddPinJoint()
                    jointY = aabb.y() + aabb.height()/2.0 - jointHeight/2.0
                    newJoint = etree.Element(addNS('rect', 'svg'))
                    newJoint.set('x', str(aabb.x() - aabb.width()/2.0 - self.space))
                    newJoint.set('y', str(jointY))
                    newJoint.set('width', str(aabb.width()+self.space))
                    newJoint.set('height', str(jointHeight))
                elif self.jointType == 'pivot':
                    ex = AddPivotJoint()
                    jointY = aabb.cy()
                    newJoint = etree.Element(addNS('path', 'svg'))
                    newJoint.set('d', getCenteredCircleSvgPath(aabb.x()-self.space/2.0, jointY, jointHeight/2.0))

                node.getparent().append(newJoint)
                newJoint.set('id', jointPrefix + str(no))

                transform = node.get('transform')
                if transform is not None:
                    newJoint.set('transform', transform)

                ex.setLabelAndStyle(blockPrefix+str(no-1), blockPrefix+str(no))
                newJoint.set(addNS('xmoto_label', 'xmoto'), ex.getLabelValue())
                newJoint.set('style', ex.getStyleValue())

        return False

if __name__ == "__main__":
    e = JointedLine()
    e.affect()
