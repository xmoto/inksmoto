from inkex import Effect
from parsers import LabelParser, StyleParser

class XmotoExtension(Effect):
    """
    if you want to change and manipulate values, use getXXXXXChanges() in your child class
    if you want to remplace values, use getXXXXXValue() in your child class
    """
    def __init__(self):
        Effect.__init__(self)

    def effect(self):
        for id, element in self.selected.iteritems():
            if element.tagName in ['path', 'rect']:
                if element.hasAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'label'):
                    self.parseLabel(element.getAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'label'))
                    self.updateInfos(self.label, self.getLabelChanges())
                    self.unparseLabel()
                    element.setAttributeNS('http://www.inkscape.org/namespaces/inkscape', 'label', self.getLabelValue())
                else:
                    self.parseLabel('')
                    self.updateInfos(self.label, self.getLabelChanges())
                    self.unparseLabel()
                    element.setAttribute('inkscape:label', self.getLabelValue())

                self.parseStyle(element.getAttribute('style'))
                self.updateInfos(self.style, self.getStyleChanges())
                self.unparseStyle()
                element.setAttribute('style', self.getStyleValue())

    def updateInfos(self, dic, *args):
        arg = args[0]
        if len(arg) > 0:
            for key, value in arg:
                dic[key] = value


    def getLabelValue(self):
        return self.labelValue

    def parseLabel(self, label):
        self.label = LabelParser().parse(label)

    def unparseLabel(self):
        self.labelValue = LabelParser().unparse(self.label)

    def getLabelChanges(self):
        return []


    def getStyleValue(self):
        return self.styleValue

    def parseStyle(self, style):
        self.style = StyleParser().parse(style)
        
    def unparseStyle(self):
        self.styleValue = StyleParser().unparse(self.style)

    def getStyleChanges(self):
        return []
