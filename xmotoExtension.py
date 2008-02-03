from inkex   import Effect, NSS, addNS
from os.path import expanduser, join, isdir
from parsers import LabelParser, StyleParser
from lxml import etree
from lxml.etree import Element
import base64
import logging, log
import os

def getInkscapeExtensionsDir():
    system = os.name
    if system == 'nt':
        # check this value from a Windows machine
        userDir = expanduser('~/Application Data/Inkscape/extensions')

        # if the userDir exists, use it. else, use the appsDir
        if isdir(userDir):
            return userDir
        else:
            return join(os.getcwd(), "share\\extensions")
    else:
        return expanduser('~/.inkscape/extensions')

class XmotoExtension(Effect):
    """
    if you want to change and manipulate values, use getXXXXXChanges() in your child class
    if you want to remplace values, use getXXXXXValue() in your child class
    """
    def __init__(self):
        Effect.__init__(self)
        self.patterns = {}
	NSS[u'xmoto'] = u'http://xmoto.tuxfamily.org/'

    def getPatterns(self):
        patterns = self.document.xpath('//pattern')
        for pattern in patterns:
            patternId = pattern.get('id')
            self.patterns[patternId] = pattern
        self.defs = self.document.xpath('/svg/defs')[0]
        self.svg  = self.document.getroot()

    def addPattern(self, textureName, textures):
        if len(self.patterns) == 0:
            self.getPatterns()

        textureName = textureName.strip(' \n')
        patternId = 'pattern_%s' % textureName
        if patternId not in self.patterns.keys():
            if textureName not in textures.keys():
		msg = 'The texture %s is not an existing one.' % textureName
                log.writeMessageToUser(msg)
		raise Exception, msg
            texture = textures[textureName]
            pattern = Element('pattern')
            for name, value in [('patternUnits', 'userSpaceOnUse'),
                                ('width', texture['width']),
                                ('height', texture['height']),
                                ('id', 'pattern_%s' % textureName)]:
                pattern.set(name, value)
            image = Element('image')
            imageAbsURL = getInkscapeExtensionsDir() + '/%s' % texture['file']
            imageFile   = open(imageAbsURL, 'rb').read()
            for name, value in [('xlink:href', 'data:image/%s;base64,%s' % (texture['file'][texture['file'].rfind('.')+1:],
                                                                            base64.encodestring(imageFile))),
                                ('width',  texture['width']),
                                ('height', texture['height']),
                                ('id', 'image_%s' % textureName),
                                ('x', '0'),
                                ('y', '0')]:
                image.set(name, value)
            pattern.append(image)
            self.patterns[patternId] = pattern
            self.defs.append(pattern)
        return patternId

    def handlePath(self, element):
        self.parseLabel(element.get(addNS('xmoto_label', 'xmoto'), ''))
        self.updateInfos(self.label, self.getLabelChanges())
        self.unparseLabel()
        element.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())

        self.generateStyle()
        self.unparseStyle()
        element.set('style', self.getStyleValue())

    def effect(self):
        for self.id, element in self.selected.iteritems():
            if element.tag in [addNS('path', 'svg'), addNS('rect', 'svg')]:
		self.handlePath(element)
	    elif element.tag in [addNS('g', 'svg')]:
		# get elements in the group
		for subelement in element.xpath('./svg:path|./svg:rect', NSS):
		    self.handlePath(subelement)

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

    def unparseStyle(self):
        self.styleValue = StyleParser().unparse(self.style)

    def generateStyle(self):
        def generateElementColor(color):
            # randomly change the color to distinguish between adjacent elements
            from random import randint
            def dec2hex(d):
                convert = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'a', 11:'b', 12:'c', 13:'d', 14:'e', 15:'f'}
                return convert[d]

            def hex2dec(x):
                convert = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
                return convert[x]

            # r, g and b must not be 'f' before adding the random int or it could became '0'
            r = (hex2dec(color[0]) + randint(0,1)) % 16
            g = (hex2dec(color[2]) + randint(0,1)) % 16
            b = (hex2dec(color[4]) + randint(0,1)) % 16
            return '#' + dec2hex(r) + color[1] + dec2hex(g) + color[3] + dec2hex(b) + color[5]

        self.style = {}
        # bad, bad, bad...
        self.parseLabel(self.getLabelValue())
        if self.label.has_key('typeid'):
            # entity or zone
            typeid = self.label['typeid']
            typeid = typeid[typeid.find('=')+1:]

            if typeid == 'PlayerStart':
                # blue
                self.style['fill'] = generateElementColor('0000ee')
            elif typeid == 'EndOfLevel':
                # yellow
                self.style['fill'] = generateElementColor('eeee00')
            elif typeid == 'ParticleSource':
                # orange
                self.style['fill'] = generateElementColor('eea500')
            elif typeid == 'Sprite':
                #        patternId = self.addPattern(self.options.name, sprites)
                #        return [('fill', 'url(#%s)' % patternId)]
                # purple
                self.style['fill'] = generateElementColor('800080')
            elif typeid == 'Strawberry':
                # red
                self.style['fill'] = generateElementColor('ee0000')
            elif typeid == 'Wrecker':
                # gray
                self.style['fill'] = generateElementColor('808080')
            elif typeid == 'Zone':
                # cyan
                self.style['fill'] = generateElementColor('00eeee')
                self.style['fill-opacity'] = 0.5
            else:
                # black
                self.style['fill'] = generateElementColor('000000')
        else:
            # block
            #        patternId = self.addPattern(self.options.texture, textures)
            #        return [('fill', 'url(#%s)' % patternId)]

            self.style['fill-opacity'] = '1'
            if self.label.has_key('position'):
                if self.label['position'].has_key('background') and self.label['position'].has_key('dynamic'):
                    # d36b00
                    self.style['fill'] = generateElementColor('d36b00')
                elif self.label['position'].has_key('background'):
                    # bdb76b = darkkhaki
                    self.style['fill'] = generateElementColor('bdb76b')
                elif self.label['position'].has_key('dynamic'):
                    # f08080 = lightcoral
                    self.style['fill'] = generateElementColor('e08080')
                else:
                    # 66cdaa = mediumaquamarine
                    self.style['fill'] = generateElementColor('66cdaa')
            else:
                # 66cdaa = mediumaquamarine
                self.style['fill'] = generateElementColor('66cdaa')

            if self.label.has_key('edge'):
                self.style['stroke-width']    = '1px'
                self.style['stroke-linecap']  = 'butt'
                self.style['stroke-linejoin'] = 'miter'
                self.style['stroke-opacity']  = '1'
                self.style['stroke']          = 'lime'
