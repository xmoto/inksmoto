from xmotoExtension import XmExt

class AddEntity(XmExt):
    def __init__(self, typeid):
        XmExt.__init__(self)
        self.typeid = typeid

    def getLabelChanges(self):
        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == self.typeid):
            self.label.clear()

        return {'typeid': self.typeid}
