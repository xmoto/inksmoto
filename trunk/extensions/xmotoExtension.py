import sys
from xmotoTools import addHomeDirInSysPath
addHomeDirInSysPath()

from inkex   import Effect, NSS, addNS
from parsers import LabelParser, StyleParser
from lxml import etree
from lxml.etree import Element
import base64
import random
import math
import logging, log
from os.path import join
from listAvailableElements import textures, sprites, particleSources
from xmotoTools import getExistingImageFullPath, createIfAbsent, getHomeInkscapeExtensionsDir, applyOnElements, getValue, getBoolValue
from svgnode import setNodeAsCircle, setNodeAsRectangle, createNewNode, exchangeParent, getParent, addNodeImage, getNodeAABB
from inksmoto_configuration import defaultCollisionRadius, svg2lvlRatio
from transform import Transform
from factory   import Factory
from matrix import Matrix

class XmotoExtension(Effect):
    def __init__(self):
        Effect.__init__(self)
        self.patterns = {}
	NSS[u'xmoto'] = u'http://xmoto.tuxfamily.org/'
        # todo::get perfect values for width and height
        sprites['PlayerStart'] = {'file':'__biker__.png', 'width':'2.10', 'height':'2.43', 'centerX':'1.05', 'centerY':'0.0'}

    def getMetaData(self):
        metadata = ''
        descriptionNode = None
        descriptionNodes = self.document.xpath('//dc:description', namespaces=NSS)
        if descriptionNodes is not None and len(descriptionNodes) > 0:
            descriptionNode = descriptionNodes[0]
	    metadata = descriptionNode.text

        return (descriptionNode, metadata)

    def getPatterns(self):
        patterns = self.document.xpath('//pattern')
        for pattern in patterns:
            patternId = pattern.get('id')
            self.patterns[patternId] = pattern
        self.defs = self.document.xpath('/svg:svg/svg:defs', namespaces=NSS)[0]
        self.svg  = self.document.getroot()

    def addImage(self, textureFilename, (w, h), (x, y), textureName):
        image = Element(addNS('image', 'svg'))
        imageAbsURL = getExistingImageFullPath(textureFilename)
        imageFile   = open(imageAbsURL, 'rb').read()
        for name, value in [(addNS('href', 'xlink'), 'data:image/%s;base64,%s' % (textureFilename[textureFilename.rfind('.')+1:],
                                                                                  base64.encodestring(imageFile))),
                            ('width',  str(w)),
                            ('height', str(h)),
                            ('id',     'image_%s_%d' % (textureName, random.randint(0, 512))),
                            ('x',      str(x)),
                            ('y',      str(y))]:
            image.set(name, value)

        return image

    def addPattern(self, textureName, textures):
        if len(self.patterns) == 0:
            self.getPatterns()

        textureWidth  = '92'
        textureHeight = '92'

        textureName = textureName.strip(' \n')
        patternId = 'pattern_%s' % textureName
        if patternId not in self.patterns.keys():
            if textureName not in textures.keys():
		msg = 'The texture %s is not an existing one.' % textureName
                log.writeMessageToUser(msg)
		raise Exception, msg
            textureFilename = textures[textureName]['file']
            pattern = Element(addNS('pattern', 'svg'))
            for name, value in [('patternUnits', 'userSpaceOnUse'),
                                ('width',        str(textureWidth)),
                                ('height',       str(textureHeight)),
                                ('id',           'pattern_%s' % textureName)]:
                pattern.set(name, value)
            image = self.addImage(textureFilename, (textureWidth, textureHeight), (0, 0), textureName)
            pattern.append(image)
            self.patterns[patternId] = pattern
            self.defs.append(pattern)
        return patternId

    def handlePath(self, node):
        self.parseLabel(node.get(addNS('xmoto_label', 'xmoto'), ''))
        self.updateInfos(self.label, self.getLabelChanges())
        self.unparseLabel()

        self.generateStyle()
        self.unparseStyle()

        self.updateNodeSvgAttributes(node)

    def setNodeAsBitmap(self, node, texName, radius, bitmaps, scale=1.0, reversed=False, rotation=0.0):
        if node.tag != addNS('g', 'svg'):
            g = createNewNode(getParent(node), 'g_'+node.get('id'), addNS('g', 'svg'))
            exchangeParent(node, g)
        else:
            g = node

        # set the xmoto_label on both the sublayer and the
        # circle (for backward compatibility)
        g.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())

        circle = g.find(addNS('path', 'svg'))
        if circle is None:
            circle = g.find(addNS('rect', 'svg'))
            if circle is None:
                raise Exception('The sprite object is neither a path nor a rect')

        circle.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())
        circle.set('style', self.getStyleValue())
        
        if g.get('style') is not None:
            del g.attrib['style']

        setNodeAsCircle(circle, scale * radius)

        # set the circle transform to the svg
        transform = circle.get('transform')
        if transform is not None:
            g.set('transform', transform)
            del circle.attrib['transform']

        image  = g.find(addNS('image', 'svg'))
        if image is not None:
            imageLabel = image.get(addNS('xmoto_label', 'xmoto'), '')
            imageLabel = LabelParser().parse(imageLabel)

            imgTexName  = getValue(imageLabel, 'param', 'name', '')

            if imgTexName != texName:
                g.remove(image)
                image = None

        cx = float(getValue(sprites, texName, 'centerX', default='0.5')) / svg2lvlRatio
        cy = float(getValue(sprites, texName, 'centerY', default='0.5')) / svg2lvlRatio

        width  = float(getValue(sprites, texName, 'width', default='1.0')) / svg2lvlRatio
        height = float(getValue(sprites, texName, 'height', default='1.0')) / svg2lvlRatio
        scaledWidth = width
        scaledHeight = height

        if scale != 1.0:
            scaledWidth  = scale * width
            scaledHeight = scale * height

        cx += (scaledWidth - width) / 2.0
        cy += (scaledHeight - height) / 2.0

        aabb = getNodeAABB(circle)
        x = aabb.cx() - cx
        # with the same coordinates, inkscape doesn't display
        # images at the same place as xmoto ...
        y = aabb.cy() - scaledHeight + cy

        if image is None:
            try:
                texFilename = bitmaps[texName]['file']
                image = self.addImage(texFilename, (scaledWidth, scaledHeight), (x, y), texName)
                # insert the image as the first child so that
                # it get displayed before the circle in inkscape
                g.insert(0, image)
            except Exception, e:
                logging.info("Can't create image for sprite %s.\n%s" % (texName, e))
        else:
            for name, value in [('width',  str(scaledWidth)),
                                ('height', str(scaledHeight)),
                                ('x',      str(x)),
                                ('y',      str(y))]:
                image.set(name, value)

        if image is not None:
            matrix = Matrix()
            if 'transform' in image.attrib:
                del image.attrib['transform']

            # translate around the origin, do the transfroms
            # then translate back.
            matrix = matrix.add_translate(aabb.cx(), aabb.cy())

            if rotation != 0.0:
                matrix = matrix.add_rotate(-rotation)
            if reversed == True:
                matrix = matrix.add_scale(-1, 1)

            matrix = matrix.add_translate(-aabb.cx(), -aabb.cy())

            if matrix != Matrix():
                transform = Factory().createObject('transform_parser').unparse(matrix.createTransform())
                image.set('transform', transform)

            # set the label on the image to check after a change
            # if the image need some change too
            image.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())

    def updateNodeSvgAttributes(self, node):
        # set svg attribute. style to change the style, d to change the path
        node.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())
        node.set('style', self.getStyleValue())

        # update node shape
        if 'typeid' in self.label:
            # entity or zone
            typeid = self.label['typeid']

            if typeid in ['PlayerStart', 'EndOfLevel', 'Strawberry', 'Wrecker']:
                if typeid == 'EndOfLevel':
                    typeid = 'Flower'

                (descriptionNode, metadata) = self.getMetaData()
                metadata = LabelParser().parse(metadata)

                texName = getValue(metadata, 'remplacement', typeid, default=typeid)
                scale = float(getValue(metadata, 'remplacement', typeid+'Scale', 1.0))
                radius = defaultCollisionRadius[typeid] / svg2lvlRatio

                self.setNodeAsBitmap(node, texName, radius, sprites, scale)

            elif typeid == 'ParticleSource':
                texName  = getValue(self.label, 'param', 'type', '')
                radius   = defaultCollisionRadius[typeid] / svg2lvlRatio

                self.setNodeAsBitmap(node, texName, radius, particleSources)

            elif typeid == 'Sprite':
                texName  = getValue(self.label, 'param', 'name', '')
                scale    = float(getValue(self.label, 'size', 'scale', 1.0))
                reversed = getBoolValue(self.label, 'position', 'reversed')
                rotation = float(getValue(self.label, 'position', 'angle', 0.0))
                radius   = defaultCollisionRadius['Sprite'] / svg2lvlRatio

                self.setNodeAsBitmap(node, texName, radius, sprites, scale, reversed, rotation)

            elif typeid == 'Zone':
                setNodeAsRectangle(node)

            elif typeid == 'Joint':
                # the addJoint extension already create the joints with the right shape
                pass

            else:
                raise Exception("typeid=%s not handled by updateNodeSvgAttributes" % typeid)

    def effect(self):
        # some extensions may need to not only manipulate the selected
        # objects in the svg (like adding new elements)
        if self.effectHook() == True:
            applyOnElements(self, self.selected, self.handlePath)

    def effectHook(self):
        return True

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
        if 'typeid' in self.label:
            # entity or zone
            typeid = self.label['typeid']

            if typeid in ['PlayerStart', 'EndOfLevel', 'ParticleSource',
                          'Sprite', 'Strawberry', 'Wrecker']:
                self.style['fill'] = 'none'
                self.style['stroke-width'] = '1px'
                self.style['stroke-linecap'] = 'butt'
                self.style['stroke-linejoin'] = 'miter'
                self.style['stroke-opacity'] = '1'

            if typeid == 'PlayerStart':
                # blue
                self.style['stroke'] = generateElementColor('0000ee')
            elif typeid == 'EndOfLevel':
                # yellow
                self.style['stroke'] = generateElementColor('eeee00')
            elif typeid == 'ParticleSource':
                # orange
                self.style['stroke'] = generateElementColor('eea500')
            elif typeid == 'Sprite':
                # purple
                self.style['stroke'] = generateElementColor('800080')
            elif typeid == 'Strawberry':
                # red
                self.style['stroke'] = generateElementColor('ee0000')
            elif typeid == 'Wrecker':
                # gray
                self.style['stroke'] = generateElementColor('808080')
            elif typeid == 'Zone':
                # cyan
                self.style['fill'] = generateElementColor('00eeee')
                self.style['fill-opacity'] = 0.5
            elif typeid == 'Joint':
                # green
                self.style['fill'] = generateElementColor('00ee00')
                if 'type' in self.label['joint'] and self.label['joint']['type'] == 'pin':
                    self.style['stroke'] = '#000000'
                    self.style['stroke-opacity'] = '1'
            else:
                # black
                self.style['fill'] = generateElementColor('000000')
        else:
            # block
            createIfAbsent(self.label, 'usetexture')
            if 'id' not in self.label['usetexture']:
                self.label['usetexture']['id'] = 'Dirt'

            # display the texture, if the texture is missing, display the old colors
            try:
                patternId = self.addPattern(self.label['usetexture']['id'], textures)
                self.style['fill'] = 'url(#%s)' % patternId
            except Exception, e:
                logging.info("Can't create pattern for texture %s.\n%s" % (self.label['usetexture']['id'], e))
                self.style['fill-opacity'] = '1'
                if 'position' in self.label:
                    if self.label['position'].has_key('background') and self.label['position'].has_key('dynamic'):
                        # d36b00
                        self.style['fill'] = generateElementColor('d36b00')
                    elif self.label['position'].has_key('background'):
                        # bdb76b = darkkhaki
                        self.style['fill'] = generateElementColor('bdb76b')
                    elif self.label['position'].has_key('dynamic'):
                        # f08080 = lightcoral
                        self.style['fill'] = generateElementColor('e08080')
                    elif self.label['position'].has_key('physics'):
                        self.style['fill'] = generateElementColor('ee00ee')
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
