from xmotoExtension import XmExt
from inkex import addNS
import log

class XmotoPaste(XmExt):
    def effectHook(self):
        if len(self.selected) == 0:
            log.outMsg("You have to select the objects whose you want to \
paste the Xmoto parameters.")
            return False
        
        (descriptionNode, metadata) = self.svg.getMetaData()
        if descriptionNode is None:
            log.outMsg("You have to copy the Xmoto properties of an \
object first.")
            return False

        label = descriptionNode.get(addNS('saved_xmoto_label', 'xmoto'))

        if label is None:
            log.outMsg("You have to copy the Xmoto properties of an \
object first.")
            return False

        for node in self.selected.values():
            node.set(addNS('xmoto_label', 'xmoto'), label)

        # we want to update the nodes shapes with their new style
        return True

def run():
    ext = XmotoPaste()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
