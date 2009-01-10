from inkex import addNS
from xmotoExtensionTkinter import XmotoExtTkElement, XmotoEntry
from svgnode import getCircleChild
from xmotoTools import checkId
import logging, log

class changeId(XmotoExtTkElement):
    def __init__(self):
        XmotoExtTkElement.__init__(self)

    def createWindow(self):
        self.defineWindowHeader('Change Id')
        self.id = XmotoEntry(self.frame, self.nodeId, label='Object id :')

    def effectLoadHook(self):
        if len(self.selected) != 1:
            log.writeMessageToUser("You have to only select the object whose you want to change the id.")
            return (True, False)

        # this extension exists to handle the case when you want to
        # change an entity id
        self.isBitmap = False

        self.node = self.selected[self.options.ids[0]]
        if self.node.tag == addNS('g', 'svg'):
            if self.node.get(addNS('xmoto_label', 'xmoto')) is None:
                # if someone group a single sprite, and then try to
                # change it's id, it will spit this on his face :
                log.writeMessageToUser("You have to only select the object whose you want to change the id.")
                return (True, False)
            else:
                self.circle = getCircleChild(self.node)
                self.isBitmap = True
                self.nodeId = self.circle.get('id', '')
        else:
            self.nodeId = self.node.get('id', '')

        return (False, False)

    def effectUnloadHook(self):
        nodeNewId = self.id.get()
        if checkId(nodeNewId) == False:
            log.writeMessageToUser("You can only use alphanumerical characters and the underscore for the id.")
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

if __name__ == "__main__":
    e = changeId()
    e.affect()
