from xmotoExtension import XmotoExtension
from inkex import addNS
import logging, log

class XmotoPaste(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def effectHook(self):
        if len(self.selected) == 0:
            log.writeMessageToUser("You have to select the objects whose you want to paste the Xmoto parameters.")
            return False
        
        (descriptionNode, metadata) = self.getMetaData()
        if descriptionNode is None:
            log.writeMessageToUser("You have to copy the Xmoto properties of an object first.")
            return False

        label = descriptionNode.get(addNS('xmoto_label', 'xmoto'))

        if label is None:
            log.writeMessageToUser("You have to copy the Xmoto properties of an object first.")
            return False

        for id, node in self.selected.iteritems():
            node.set(addNS('xmoto_label', 'xmoto'), label)

        # we want to update the nodes shapes with their new style
        return True

if __name__ == "__main__":
    e = XmotoPaste()
    e.affect()
