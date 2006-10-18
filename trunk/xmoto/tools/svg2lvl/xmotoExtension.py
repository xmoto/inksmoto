from inkex   import Effect, NSS
from os.path import expanduser
from parsers import LabelParser, StyleParser
import xml.dom.Element
import listAvailableElements
import base64
import logging, log

class XmotoExtension(Effect):
    """
    if you want to change and manipulate values, use getXXXXXChanges() in your child class
    if you want to remplace values, use getXXXXXValue() in your child class
    """
    def __init__(self):
        Effect.__init__(self)
        self.patterns = {}

    def getPatterns(self):
        patterns = self.document.getElementsByTagName('patterns')
        for pattern in patterns:
            patternId = pattern.attributes.getNamedItem('id').nodeValue
            self.patterns[patternId] = pattern
        self.defs = self.document.getElementsByTagName('defs')[0]
        self.svg  = self.document.getElementsByTagName('svg')[0]
        if not self.svg.hasAttributeNS('http://www.w3.org/2000/xmlns/', 'xlink'):
            self.svg.setAttribute('xmlns:xlink', NSS['xlink'])

    def addPattern(self, texture):
        if len(self.patterns) == 0:
            self.getPatterns()
        
        if texture == 'default':
            texture = listAvailableElements.default
        patternId = 'pattern_%s' % texture
        if patternId not in self.patterns.keys():
            if texture not in listAvailableElements.textures:
                log.writeMessageToUser('The texture %s is not an existing one.')
            pattern = xml.dom.Element.Element(self.defs.ownerDocument, 'pattern', None, None, None)
            for name, value in [('patternUnits', 'userSpaceOnUse'),
                                ('width', '26'), ('height', '26'),
                                ('id', 'pattern_%s' % texture)]:
                pattern.setAttribute(name, value)
            image = xml.dom.Element.Element(self.defs.ownerDocument, 'image', None, None, None)
            imageAbsURL = expanduser('~/.inkscape/extensions/textures/%s.jpg' % texture)
            imageFile   = open(imageAbsURL, 'rb').read()
            for name, value in [('xlink:href', 'data:image/png;base64,%s' % (base64.encodestring(imageFile))),
                                ('width', '26'),
                                ('height', '26'),
                                ('id', 'image_%s' % texture),
                                ('x', '0'),
                                ('y', '0')]:
                image.setAttribute(name, value)
            pattern.appendChild(image)
            self.patterns[patternId] = pattern
            self.defs.appendChild(pattern)
        return patternId

    def effect(self):
        for self.id, element in self.selected.iteritems():
            if element.tagName in ['path', 'rect']:
                self.parseStyle(element.getAttribute('style'))
                if element.hasAttributeNS(NSS['inkscape'], 'label'):
                    self.parseLabel(element.getAttributeNS(NSS['inkscape'], 'label'))
                    self.updateInfos(self.label, self.getLabelChanges())
                    self.unparseLabel()
                    element.setAttributeNS(NSS['inkscape'], 'label', self.getLabelValue())
                else:
                    self.parseLabel('')
                    self.updateInfos(self.label, self.getLabelChanges())
                    self.unparseLabel()
                    element.setAttribute('inkscape:label', self.getLabelValue())

                self.updateInfos(self.style, self.getStyleChanges())
                self.unparseStyle()
                element.setAttribute('style', self.getStyleValue())

    def updateInfos(self, dic, *args):
	# the first args element is the tab with the changes
	# it can be empty if there's no changes.
        arg = args[0]
        if len(arg) > 0:
            for key, value in arg:
		if type(value) == dict:
                    namespace = key
                    for key,value in value.iteritems():
                        if not dic.has_key(namespace):
                            dic[namespace] = {}
                        dic[namespace][key] = value
		else:
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
