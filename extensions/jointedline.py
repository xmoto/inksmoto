#!/usr/bin/python
"""
Copyright (C) 2008,2009 Emmanuel Gorse, e.gorse@gmail.com
Copyright (C) 2008,2009 Ville Lahdenvuo, tuhoojabotti@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from inksmoto.inkex import addNS
from inksmoto.xmotoExtension import XmExt
from inksmoto.xmotoTools import createIfAbsent
from inksmoto.addJoint import AddJoint
from inksmoto.svgnode import getCenteredCircleSvgPath, convertToXmNode
from lxml import etree
from inksmoto import log

class JointedLine(XmExt):
    def __init__(self):
        XmExt.__init__(self)

        self.OptionParser.add_option("-s", "--space", type="float",
                                     dest="space", help="space between blocks")
        self.OptionParser.add_option("-j", "--joint", type="string",
                                     dest="joint", help="type of joint")
        self.OptionParser.add_option("-b", "--blocks", type="int",
                                     dest="blocks",
                                     help="number of blocks in the line")

    def effectHook(self):
        #read svg information, find selected path to use in the line.
        if len(self.selected) != 1:
            log.outMsg("You have to select only one object.")
            return False

        for node in self.selected.values():
            if node.tag not in [addNS('path', 'svg'), addNS('rect', 'svg')]:
                log.outMsg("You need to select path and rectangle only.")
                return False

        # there's only one selected object
        node = self.selected.values()[0]

        self.jointType = self.options.joint
        self.space     = self.options.space
        self.numBlocks = self.options.blocks

        # is it a physic block?
        node = convertToXmNode(node, self.svg)
        label = node.getParsedLabel()
        createIfAbsent(label, 'position')
        if 'physics' not in label['position']:
            log.outMsg("The selected object has to be an Xmoto physics block.")
            return False

        # we need uniq ids
        idPrefix = node.get('id')
        blockPrefix = idPrefix + 'jl_block'
        jointPrefix = idPrefix + 'jl_joint'

        # TODO::if called different times on the same object
        node.set('id', blockPrefix + '0')

        aabb = node.getAABB()
        offset = self.space + aabb.width()
        jointHeight = 10
        if jointHeight > aabb.height()/2.0:
            jointHeight = aabb.height()/2.0

        ex = AddJoint(self.jointType)
        for no in xrange(1, self.numBlocks+1):
            node = node.duplicate(blockPrefix+str(no))
            node.translate(offset, 0)

            if no < self.numBlocks+1:
                newJoint = None
                if self.jointType == 'pin':
                    jointX = aabb.x() - aabb.width()/2.0 - self.space
                    jointY = aabb.y() + aabb.height()/2.0 - jointHeight/2.0
                    jointWidth = aabb.width()+self.space
                    newJoint = etree.Element(addNS('rect', 'svg'))
                    newJoint.set('x', str(jointX))
                    newJoint.set('y', str(jointY))
                    newJoint.set('width', str(jointWidth))
                    newJoint.set('height', str(jointHeight))
                elif self.jointType == 'pivot':
                    jointX = aabb.x()-self.space/2.0
                    jointY = aabb.cy()
                    newJoint = etree.Element(addNS('path', 'svg'))
                    newJoint.set('d', getCenteredCircleSvgPath(jointX,
                                                               jointY,
                                                               jointHeight/2.0))

                node.getparent().append(newJoint)
                newJoint.set('id', jointPrefix + str(no))

                transform = node.get('transform')
                if transform is not None:
                    newJoint.set('transform', transform)

                label, style = ex.getLabelAndStyle(blockPrefix+str(no-1),
                                                   blockPrefix+str(no))
                ex.updateNodeSvgAttributes(newJoint, label, style)

        return False

def run():
    ext = JointedLine()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
