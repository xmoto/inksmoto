from inkex   import Effect, NSS
from os.path import expanduser
from parsers import LabelParser, StyleParser
import xml.dom.Element
import base64
import logging, log
import os

class XmotoExtension(Effect):
    """
    if you want to change and manipulate values, use getXXXXXChanges() in your child class
    if you want to remplace values, use getXXXXXValue() in your child class
    """
    def __init__(self):
        Effect.__init__(self)
        self.patterns = {}

    def getInkscapeExtensionsDir(self):
        system = os.name
        if system == 'nt':
            # check this value from a Windows machine
            return expanduser('~/Application Data/inkscape/extensions')
        else:
            return expanduser('~/.inkscape/extensions')

    def getPatterns(self):
        patterns = self.document.getElementsByTagName('patterns')
        for pattern in patterns:
            patternId = pattern.attributes.getNamedItem('id').nodeValue
            self.patterns[patternId] = pattern
        self.defs = self.document.getElementsByTagName('defs')[0]
        self.svg  = self.document.getElementsByTagName('svg')[0]
        if not self.svg.hasAttributeNS('http://www.w3.org/2000/xmlns/', 'xlink'):
            self.svg.setAttribute('xmlns:xlink', NSS['xlink'])

    def addPattern(self, textureName, textures):
        if len(self.patterns) == 0:
            self.getPatterns()

        textureName = textureName.strip(' \n')
        patternId = 'pattern_%s' % textureName
        if patternId not in self.patterns.keys():
            if textureName not in textures.keys():
                log.writeMessageToUser('The texture %s is not an existing one.' % textureName)
            texture = textures[textureName]
            pattern = xml.dom.Element.Element(self.defs.ownerDocument, 'pattern', None, None, None)
            for name, value in [('patternUnits', 'userSpaceOnUse'),
                                ('width', texture['width']),
                                ('height', texture['height']),
                                ('id', 'pattern_%s' % textureName)]:
                pattern.setAttribute(name, value)
            image = xml.dom.Element.Element(self.defs.ownerDocument, 'image', None, None, None)
            imageAbsURL = self.getInkscapeExtensionsDir() + '/%s' % texture['file']
            imageFile   = open(imageAbsURL, 'rb').read()
            for name, value in [('xlink:href', 'data:image/%s;base64,%s' % (texture['file'][texture['file'].rfind('.')+1:],
                                                                            base64.encodestring(imageFile))),
                                ('width',  texture['width']),
                                ('height', texture['height']),
                                ('id', 'image_%s' % textureName),
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
                #self.parseStyle(element.getAttribute('style'))
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

                #self.updateInfos(self.style, self.getStyleChanges())
                self.generateStyle()
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

#    def parseStyle(self, style):
#        self.style = StyleParser().parse(style)
        
    def unparseStyle(self):
        self.styleValue = StyleParser().unparse(self.style)

    def generateStyle(self):
        self.style = {}
        # bad, bad, bad...
        self.parseLabel(self.getLabelValue())
        if self.label.has_key('typeid'):
            # entity or zone
            typeid = self.label['typeid']
            typeid = typeid[typeid.find('=')+1:]

            if typeid == 'PlayerStart':
                self.style['fill'] = 'blue'
            elif typeid == 'EndOfLevel':
                self.style['fill'] = 'yellow'
            elif typeid == 'ParticleSource':
                self.style['fill'] = 'orange'
            elif typeid == 'Sprite':
                #        patternId = self.addPattern(self.options.name, sprites)
                #        return [('fill', 'url(#%s)' % patternId)]
                self.style['fill'] = 'purple'
            elif typeid == 'Strawberry':
                self.style['fill'] = 'red'
            elif typeid == 'Wrecker':
                self.style['fill'] = 'gray'
            elif typeid == 'Zone':
                self.style['fill'] = 'cyan'
            else:
                self.style['fill'] = 'black'
        else:
            # block
            #        patternId = self.addPattern(self.options.texture, textures)
            #        return [('fill', 'url(#%s)' % patternId)]

            # normal block
            self.style['fill'] = 'mediumaquamarine'
            if self.label.has_key('position'):
                if self.label['position'].has_key('background'):
                    self.style['fill'] = 'darkkhaki'
                elif self.label['position'].has_key('dynamic'):
                    self.style['fill'] = 'lightcoral'

            if self.label.has_key('edge'):
                self.style['stroke-width']    = '1px'
                self.style['stroke-linecap']  = 'butt'
                self.style['stroke-linejoin'] = 'miter'
                self.style['stroke-opacity']  = '1'
                self.style['stroke']          = 'lime'


### styles:
#
# block:change texture
#    def getStyleChanges(self):
#        patternId = self.addPattern(self.options.texture, textures)
#        return [('fill', 'url(#%s)' % patternId)]
#
# block:background
#    def getStyleChanges(self):
#        patternId = self.addPattern(self.options.texture, textures)
#        return [('fill', 'url(#%s)' % patternId)]
#
# block:dynamic
#    def getStyleChanges(self):
#        if not self.label.has_key('edge'):
#            self.style.clear()
#        return [('fill', 'lightcoral')]
#
# block:edge (add)
#    def getStyleChanges(self):
#        return [('stroke-width',    '1px'),   ('stroke-linecap', 'butt'),
#                ('stroke-linejoin', 'miter'), ('stroke-opacity', '1'),
#                ('stroke',          'lime')]
# 
# block:edge (add)
#
#    def getStyleChanges(self):
#        if self.label.has_key('typeid'):
#            return []
#
#        self.style.clear()
#        if self.label.has_key('position'):
#            if self.label['position'].has_key('dynamic'):
#                fillColor = 'lightcoral'
#            else:
#                fillColor = 'darkkhaki'
#        else:
#            fillColor = 'mediumaquamarine'
#        return [('fill', fillColor)]
#
# block:normal
#    def getStyleChanges(self):
#        if not self.label.has_key('edge'):
#            self.style.clear()
#        return [('fill', 'mediumaquamarine')]
#
# entity:end
#    def getStyleChanges(self):
#	self.style.clear()
#        return [('fill', 'yellow')]
#
# entity:particle source
#    def getStyleChanges(self):
#        return [('fill', 'orange')]
#
# entity:player start
#    def getStyleChanges(self):
#        self.style.clear()
#        return [('fill', 'blue')]
#
# entity:sprite
#    def getStyleChanges(self):
#        patternId = self.addPattern(self.options.name, sprites)
#        return [('fill', 'url(#%s)' % patternId)]
#
# entity:strawberry
#    def getStyleChanges(self):
#        self.style.clear()
#        return [('fill', 'red')]
#
# entity:wrecker
#    def getStyleChanges(self):
#        self.style.clear()
#        return [('fill', 'gray')]
#
# entity:zone
#    def getStyleChanges(self):
#        self.style.clear()
#        return [('fill', 'cyan')]
#
