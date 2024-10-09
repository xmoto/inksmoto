#!/usr/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from gi.repository import Gtk
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
        # Populate the objectId field with the node ID
        self.get('objectId').set_text(self.nodeId)

    def getSignals(self):
        return {}

    def effectLoadHook(self):
        def setSublayerAttrs():
            self.node = convertToXmNode(self.node, self.svg)
            self.circle = self.node.getCircleChild()
            self.isBitmap = True
            self.nodeId = self.circle.get('id', '')

        if len(self.selected) != 1:
            log.outMsg("You have to select exactly one object whose ID you want to change.")
            return (True, False)

        self.isBitmap = False
        self.node = self.selected[self.options.ids[0]]

        if self.node.tag == addNS('g', 'svg'):
            if self.node.get(addNS('xmoto_label', 'xmoto')) is None:
                log.outMsg("Invalid selection: you must select a sublayer entity.")
                return (True, False)
            else:
                setSublayerAttrs()
        elif self.node.tag in [addNS('use', 'svg'), addNS('image', 'svg')]:
            if self.node.getparent().tag != addNS('g', 'svg'):
                log.outMsg("Selected image is not part of a sublayer entity.")
                return (True, False)
            else:
                self.node = self.node.getparent()
                setSublayerAttrs()
        else:
            self.nodeId = self.node.get('id', '')

        return (False, False)

    def effectUnloadHook(self):
        nodeNewId = self.get('objectId').get_text()
        if not checkVarId(nodeNewId):
            log.outMsg("ID can only contain alphanumeric characters and underscores, and must not begin with a number.")
            return False

        if nodeNewId != self.nodeId:
            if self.isBitmap:
                self.circle.set('id', nodeNewId)
                self.node.set('id', 'g_' + nodeNewId)
                image = self.node.find(addNS('image', 'svg'))
                if image is not None:
                    image.set('id', 'image_' + nodeNewId)
            else:
                self.node.set('id', nodeNewId)

        return False

def run():
    ext = ChangeId()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
