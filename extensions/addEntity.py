from xmotoExtension import XmotoExtension

class AddEntity(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def getLabelChanges(self):
        changes = []

        # previously not the right entity
        if not ('typeid' in self.label and self.label['typeid'] == self.typeid):
            self.label.clear()

        changes.append(['typeid', self.typeid])

        return changes
