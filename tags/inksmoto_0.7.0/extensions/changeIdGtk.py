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

from inksmoto.inkex import addNS
from inksmoto.xmExtGtk import XmExtGtkElement
from inksmoto import xmGuiGtk
from inksmoto.svgnode import XmNode, convertToXmNode
from inksmoto.xmotoTools import checkVarId
from inksmoto.factory import Factory
from inksmoto import log

class ChangeId(XmExtGtkElement):
    def getWindowInfos(self):
        gladeFile = "changeId.glade"
        windowName = "changeId"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        # not really beautiful. easier code than doing a special case
        # to return {'objectId': self.nodeId} because we don't fill
        # self.comVal
        self.get('objectId').set_text(self.nodeId)

    def effectLoadHook(self):
        def setSublayerAttrs():
            self.node = convertToXmNode(self.node, self.svg)
            self.circle = self.node.getCircleChild()
            self.isBitmap = True
            self.nodeId = self.circle.get('id', '')

        if len(self.selected) != 1:
            log.outMsg("You have to only select the object whose you want to \
change the id.")
            return (True, False)

        # this extension exists to handle the case when you want to
        # change an entity id
        self.isBitmap = False

        self.node = self.selected[self.options.ids[0]]
        if self.node.tag == addNS('g', 'svg'):
            if self.node.get(addNS('xmoto_label', 'xmoto')) is None:
                # if someone group a single sprite, and then try to
                # change it's id, it will spit this on his face :
                log.outMsg("You have to only select the object whose you want \
to change the id.")
                return (True, False)
            else:
                setSublayerAttrs()
        elif self.node.tag in [addNS('use', 'svg'), addNS('image', 'svg')]:
            if self.node.getparent().tag != addNS('g', 'svg'):
                log.outMsg("You have selected an image which is not part of a \
sublayer entity.\nStop doing that.")
                return (True, False)
            else:
                self.node = self.node.getparent()
                setSublayerAttrs()
        else:
            self.nodeId = self.node.get('id', '')

        return (False, False)

    def effectUnloadHook(self):
        nodeNewId = self.get('objectId').get_text()
        if checkVarId(nodeNewId) == False:
            log.outMsg("You can only use alphanumerical characters and the \
underscore for the id.\nThe id can't begin with a number.")
            return False

        if nodeNewId != self.nodeId:
            if self.isBitmap == True:
                self.circle.set('id', nodeNewId)
                self.node.set('id', 'g_'+nodeNewId)
                image  = self.node.find(addNS('image', 'svg'))
                if image is not None:
                    image.set('id', 'image_'+nodeNewId)
            else:
                self.node.set('id', nodeNewId)

        return False

def run():
    ext = ChangeId()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
