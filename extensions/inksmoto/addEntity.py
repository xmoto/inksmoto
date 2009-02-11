from xmotoExtension import XmExt

class AddEntity(XmExt):
    def __init__(self, typeid):
        XmExt.__init__(self)
        self.typeid = typeid

    def getNewLabel(self, label):
        return {'typeid': self.typeid}
