from inkex import addNS
from xmotoExtension import XmotoExtension
import logging, log

class XmotoCopy(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def effectHook(self):
        if len(self.selected) != 1:
            log.writeMessageToUser("You have to only select the object whose you want to copy the Xmoto parameters.")
            return False

        node = self.selected[self.options.ids[0]]
        label = node.get(addNS('xmoto_label', 'xmoto'))

        if label is None:
            log.writeMessageToUser("The selected object has no Xmoto properties to copy.")
            return False

        (descriptionNode, metadata) = self.getMetaData()
        if descriptionNode is None:
            self.createMetadata('')
            (descriptionNode, metadata) = self.getMetaData()

        descriptionNode.set(addNS('xmoto_label', 'xmoto'), label)

        return False

if __name__ == "__main__":
    e = XmotoCopy()
    e.affect()
