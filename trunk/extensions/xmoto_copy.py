from inksmoto.inkex import addNS
from inksmoto.xmotoExtension import XmExt
from inksmoto import log

class XmotoCopy(XmExt):
    def effectHook(self):
        if len(self.selected) != 1:
            log.outMsg("You have to only select the object whose you want \
to copy the Xmoto parameters.")
            return False

        node = self.selected[self.options.ids[0]]
        label = node.get(addNS('xmoto_label', 'xmoto'))

        if label is None:
            log.outMsg("The selected object has no Xmoto properties to copy.")
            return False

        node = self.svg.getAndCreateMetadataNode()
        node.set(addNS('saved_xmoto_label', 'xmoto'), label)

        return False

def run():
    ext = XmotoCopy()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
