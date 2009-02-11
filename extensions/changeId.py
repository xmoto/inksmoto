from inksmoto.inkex import addNS
from inksmoto.xmotoExtensionTkinter import XmExtTkElement
from inksmoto.svgnode import getCircleChild
from inksmoto.xmotoTools import checkId
from inksmoto import xmGui
from inksmoto.factory import Factory
from inksmoto import log

class ChangeId(XmExtTkElement):
    def __init__(self):
        XmExtTkElement.__init__(self)

    def createWindow(self):
        f = Factory()

        xmGui.defineWindowHeader('Change Id')
        self.objectId = f.createObject('XmEntry', self.nodeId, label='Object id :')

    def effectLoadHook(self):
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
                self.circle = getCircleChild(self.node)
                self.isBitmap = True
                self.nodeId = self.circle.get('id', '')
        else:
            self.nodeId = self.node.get('id', '')

        return (False, False)

    def effectUnloadHook(self):
        nodeNewId = self.objectId.get()
        if checkId(nodeNewId) == False:
            log.outMsg("You can only use alphanumerical characters and the \
underscore for the id.")
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
