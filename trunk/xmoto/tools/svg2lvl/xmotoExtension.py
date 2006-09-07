from inkex import Effect
from parsers import LabelParser

class XmotoExtension(Effect):
    """
    if you want to change and manipulate values, use getChanges() in your child class
    if you want to remplace values, use getLabelValue() in your child class
    """
    def __init__(self):
        Effect.__init__(self)

    def effect(self):
        for id, element in self.selected.iteritems():
            if element.tagName == 'path':
                if element.hasAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'label'):
                    self.parseLabel(element.getAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'label'))
                    self.updateInfos(self.getChanges())
                    self.unparseLabel()
                    element.setAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'label', self.getLabelValue())
                else:
                    self.parseLabel('')
                    self.updateInfos(self.getChanges())
                    self.unparseLabel()
                    element.setAttribute('inkscape:label', self.getLabelValue())

    def getLabelValue(self):
        return self.labelValue

    def parseLabel(self, label):
        self.dic = LabelParser().parse(label)

    def updateInfos(self, *args):
        arg = args[0]
        if len(arg) > 0:
            for key, value in arg:
                self.dic[key] = value

    def unparseLabel(self):
        self.labelValue = LabelParser().unparse(self.dic)

    def getChanges(self):
        return []
