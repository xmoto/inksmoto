from xmotoExtension import XmotoExtension
from inkex import addNS

class AddEntity(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == self.typeid):
            self.label.clear()

        return {'typeid': self.typeid}
