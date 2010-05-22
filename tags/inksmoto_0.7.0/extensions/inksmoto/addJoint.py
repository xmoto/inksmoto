#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

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

from xmotoExtension import XmExt
from inkex import addNS
from svgnode import createNewNode, getJointPath, XmNode
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
            label = XmNode(node).getParsedLabel()
            createIfAbsent(label, 'position')
            if 'physics' not in label['position']:
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

        label, style = self.getLabelAndStyle(block1Id, block2Id)
        self.updateNodeSvgAttributes(anchorNode, label, style)

        return False

    def createJointNode(self, parent, jid, block1, block2):
        aabb1 = XmNode(block1, self.svg).getAABB()
        aabb1.applyTransform(block1.get('transform', ''))
        aabb2 = XmNode(block2, self.svg).getAABB()
        aabb2.applyTransform(block2.get('transform', ''))

        tag = addNS('path', 'svg')
        node = createNewNode(parent, jid, tag)
        node.set('d', getJointPath(self.jointType, aabb1, aabb2))

        return node

    def getLabelAndStyle(self, block1Id, block2Id):
        label = {'typeid':'Joint',
                 'joint':
                     {'type':'%s' % self.jointType,
                      'connection-start':block1Id,
                      'connection-end':block2Id
                      }
                 }

        style = self.generateStyle(label)

        return label, style
