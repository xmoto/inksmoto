from xmotoExtension import XmotoExtension
from inkex import addNS
import log

class AddPivotJoint(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def effectHook(self):
        """ we need to manipulate the three selected items,
        so we redefine this function """

        # we need three selected items:
        # -block 1
        # -block 2
        # -the anchor
        if len(self.selected) != 3:
            log.writeMessageToUser("You have to select three objects.")
            return

        # check that the objects are paths or rectangles
        for (id, node) in self.selected.iteritems():
            if node.tag not in [addNS('path', 'svg'), addNS('rect', 'svg')]:
                log.writeMessageToUser("You need to select path and rectangle only.")
                return

        # ids are given to inksmoto in the selection order.
        # the anchor is the last selected
        anchorId = self.options.ids[-1]
        anchorNode = self.selected[anchorId]
        block1Id = self.options.ids[0]
        block2Id = self.options.ids[1]

        self.setLabelAndStyle(block1Id, block2Id)
        anchorNode.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())
        anchorNode.set('style', self.getStyleValue())

    def setLabelAndStyle(self, block1Id, block2Id):
        self.label = {'typeid':'Joint',
                      'joint':
                      {'type':'pivot',
                       'connection-start':block1Id,
                       'connection-end':block2Id
                      }
                     }

        self.unparseLabel()
        self.generateStyle()
        self.unparseStyle()

if __name__ == "__main__":
    e = AddPivotJoint()
    e.affect()
