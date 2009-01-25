from xmotoExtension import XmotoExtension

class AddEntity(XmotoExtension):
    def __init__(self, typeid):
        XmotoExtension.__init__(self)
        self.typeid = typeid

    def getLabelChanges(self):
        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == self.typeid):
            self.label.clear()

        return {'typeid': self.typeid}
