import sys
from xmotoTools import addHomeDirInSysPath
addHomeDirInSysPath()

from inkex   import Effect, NSS, addNS
from parsers import LabelParser, StyleParser
import logging
from listAvailableElements import TEXTURES, SPRITES, PARTICLESOURCES
from xmotoTools import createIfAbsent, applyOnElements, getBoolValue
from xmotoTools import getValue, setOrDelBool, delWithoutExcept
from xmotoTools import setOrDelBitmap
from svgnode import setNodeAsCircle, setNodeAsRectangle, createNewNode
from svgnode import newParent, newImageNode, getNodeAABB, getCircleChild
from inksmoto_configuration import ENTITY_RADIUS, SVG2LVL_RATIO
from factory import Factory
from matrix import Matrix
from svgDoc import SvgDoc

class XmExt(Effect):
    def __init__(self):
        Effect.__init__(self)
        NSS[u'xmoto'] = u'http://xmoto.tuxfamily.org/'
        # in the svgs created by inkscape 0.46, in the cc:Work node,
        # the cc refers to the creativecommons namespace, not the
        # web.resource one put in inkex
        NSS[u'cc'] = u'http://creativecommons.org/ns#'
        # todo::get perfect values for width and height
        SPRITES['PlayerStart'] = {'file':'__biker__.png',
                                  'width':'2.10',
                                  'height':'2.43',
                                  'centerX':'1.05',
                                  'centerY':'0.0'}
        # default values to populate windows
        self.defaultValues = {}
        self.svg = SvgDoc()

    def loadDefaultValues(self):
        (node, value) = self.svg.getMetaData()
        if node is not None:
            defaultLabel = node.get(addNS('default_xmoto_label', 'xmoto'))
            if defaultLabel is not None:
                self.defaultValues = LabelParser().parse(defaultLabel)

    def unloadDefaultValues(self):
        self.updateInfos(self.defaultValues, self.label)

        if len(self.defaultValues.keys()) == 0:
            return

        defaultLabel = LabelParser().unparse(self.defaultValues)
        (node, value) = self.svg.getAndCreateMetadata()
        node.set(addNS('default_xmoto_label', 'xmoto'), defaultLabel)

    def getValue(self, dictValues, namespace, name=None, default=None):
        value = getValue(dictValues, namespace, name, None)
        if value is None:
            value = getValue(self.defaultValues, namespace, name, None)
            if value is None:
                return default
            else:
                return value
        else:
            return value

    def setOrDelBool(self, _dict, namespace, widget, key):
        if setOrDelBool(_dict[namespace], widget, key) == False:
            delWithoutExcept(self.defaultValues, key, namespace)

    def setOrDelBitmap(self, _dict, namespace, key, button):
        if setOrDelBitmap(_dict[namespace], key, button) == False:
            delWithoutExcept(self.defaultValues, key, namespace)

    def handlePath(self, node):
        self.parseLabel(node.get(addNS('xmoto_label', 'xmoto'), ''))
        self.updateInfos(self.label, self.getLabelChanges())
        self.unparseLabel()

        self.generateStyle()
        self.unparseStyle()

        self.updateNodeSvgAttributes(node)

    def setNodeAsBitmap(self, node, texName, radius, bitmaps,
                        scale=1.0, _reversed=False, rotation=0.0):
        if node.tag != addNS('g', 'svg'):
            # the user selected the circle or the image instead of the
            # sublayer
            if node.tag == addNS('image', 'svg'):
                _id = node.get('id', '')
                pos = _id.find('_')
                parentId = 'g_'+_id[pos+1:]
            else:
                parentId = 'g_'+node.get('id', '')

            if node.getparent().get('id', '') == parentId:
                g = node.getparent()
            else:
                g = createNewNode(node.getparent(), parentId, addNS('g', 'svg'))
                newParent(node, g)
        else:
            g = node

        # set the xmoto_label on both the sublayer and the
        # circle (for backward compatibility)
        g.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())

        try:
            circle = getCircleChild(g)
        except Exception, e:
            _id = g.get('id', '')
            logging.warning("Sprite [%s] is an empty layer\n%s" % (_id, e))
            return

        circle.set(addNS('xmoto_label', 'xmoto'), self.getLabelValue())
        circle.set('style', self.getStyleValue())
        
        if g.get('style') is not None:
            del g.attrib['style']

        setNodeAsCircle(circle, scale * radius)

        # set the circle transform to the layer
        transform = circle.get('transform')
        if transform is not None:
            g.set('transform', transform)
            del circle.attrib['transform']

        image  = g.find(addNS('image', 'svg'))
        if image is not None:
            imageLabel = image.get(addNS('saved_xmoto_label', 'xmoto'), '')
            imageLabel = LabelParser().parse(imageLabel)

            imgTexName  = self.getValue(imageLabel, 'param', 'name', '')

            if imgTexName != texName:
                g.remove(image)
                image = None

        infos = self.getValue(SPRITES, texName)
        cx = float(self.getValue(infos,
                                 'centerX',
                                 default='0.5')) / SVG2LVL_RATIO
        cy = float(self.getValue(infos,
                                 'centerY',
                                 default='0.5')) / SVG2LVL_RATIO

        width  = float(self.getValue(infos,
                                     'width',
                                     default='1.0')) / SVG2LVL_RATIO
        height = float(self.getValue(infos,
                                     'height',
                                     default='1.0')) / SVG2LVL_RATIO
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
                image = newImageNode(texFilename,
                                     (scaledWidth, scaledHeight),
                                     (x, y),
                                     texName)
                image.set('id', 'image_' + circle.get('id'))
                # insert the image as the first child so that
                # it get displayed before the circle in inkscape
                g.insert(0, image)
            except Exception, e:
                logging.info("Can't create image for sprite %s.\n%s"
                             % (texName, e))
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
            if _reversed == True:
                matrix = matrix.add_scale(-1, 1)

            matrix = matrix.add_translate(-aabb.cx(), -aabb.cy())

            if matrix != Matrix():
                parser = Factory().createObject('transform_parser')
                transform = parser.unparse(matrix.createTransform())
                image.set('transform', transform)

            # set the label on the image to check after a change
            # if the image need some change too
            image.set(addNS('saved_xmoto_label', 'xmoto'),
                      self.getLabelValue())

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

                (descriptionNode, metadata) = self.svg.getMetaData()
                metadata = LabelParser().parse(metadata)

                texName = self.getValue(metadata, 'remplacement',
                                        typeid, default=typeid)
                scale = float(self.getValue(metadata, 'remplacement',
                                            typeid+'Scale', 1.0))
                _reversed = getBoolValue(self.label, 'position', 'reversed')
                rotation = float(self.getValue(self.label, 'position',
                                               'angle', 0.0))
                radius = ENTITY_RADIUS[typeid] / SVG2LVL_RATIO

                self.setNodeAsBitmap(node, texName, radius, SPRITES,
                                     scale, _reversed, rotation)

            elif typeid == 'ParticleSource':
                texName  = self.getValue(self.label, 'param', 'type', '')
                radius   = ENTITY_RADIUS[typeid] / SVG2LVL_RATIO

                self.setNodeAsBitmap(node, texName, radius, PARTICLESOURCES)

            elif typeid == 'Sprite':
                texName = self.getValue(self.label, 'param', 'name', '')
                scale = float(self.getValue(self.label, 'size', 'scale', 1.0))
                _reversed = getBoolValue(self.label, 'position', 'reversed')
                rotation = float(self.getValue(self.label, 'position',
                                               'angle', 0.0))
                radius   = ENTITY_RADIUS['Sprite'] / SVG2LVL_RATIO

                self.setNodeAsBitmap(node, texName, radius, SPRITES,
                                     scale, _reversed, rotation)

            elif typeid == 'Zone':
                setNodeAsRectangle(node)

            elif typeid == 'Joint':
                # the addJoint extension already create the joints
                # with the right shape
                pass

            else:
                raise Exception("typeid=%s not handled by \
updateNodeSvgAttributes" % typeid)

    def effect(self):
        self.svg.setDoc(self.document)

        # some extensions may need to not only manipulate the selected
        # objects in the svg (like adding new elements)
        if self.effectHook() == True:
            applyOnElements(self, self.selected, self.handlePath)

    def effectHook(self):
        return True

    def updateInfos(self, toUpdate, newValues):
        for key, value in newValues.iteritems():
            if type(value) == dict:
                namespace = key
                for key, value in value.iteritems():
                    createIfAbsent(toUpdate, namespace)
                    toUpdate[namespace][key] = value
            else:
                toUpdate[key] = value

    def getLabelValue(self):
        return self.labelValue

    def parseLabel(self, label):
        self.label = LabelParser().parse(label)

    def unparseLabel(self):
        self.labelValue = LabelParser().unparse(self.label)

    def getLabelChanges(self):
        return {}

    def getStyleValue(self):
        return self.styleValue

    def unparseStyle(self):
        self.styleValue = StyleParser().unparse(self.style)

    def generateStyle(self):
        def generateElementColor(color):
            """ randomly change the color to distinguish between
            adjacent elements"""
            from random import randint
            def dec2hex(d):
                convert = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5',
                           6:'6', 7:'7', 8:'8', 9:'9', 10:'a', 11:'b',
                           12:'c', 13:'d', 14:'e', 15:'f'}
                return convert[d]

            def hex2dec(x):
                convert = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5,
                           '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11,
                           'c':12, 'd':13, 'e':14, 'f':15}
                return convert[x]

            # r, g and b must not be 'f' before adding the random int
            # or it could became '0'
            r = (hex2dec(color[0]) + randint(0, 1)) % 16
            g = (hex2dec(color[2]) + randint(0, 1)) % 16
            b = (hex2dec(color[4]) + randint(0, 1)) % 16
            return ('#' + dec2hex(r) + color[1]
                    + dec2hex(g) + color[3]
                    + dec2hex(b) + color[5])

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
                if getValue(self.label, 'joint', 'type', '') == 'pin':
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

            # display the texture, if the texture is missing, display
            # the old colors
            try:
                patternId = self.svg.addPattern(self.label['usetexture']['id'],
                                            TEXTURES)
                self.style['fill'] = 'url(#%s)' % patternId
            except Exception, e:
                logging.info("Can't create pattern for texture %s.\n%s"
                             % (self.label['usetexture']['id'], e))
                self.style['fill-opacity'] = '1'
                if 'position' in self.label:
                    if ('background' in self.label['position']
                        and 'dynamic' in self.label['position']):
                        # d36b00
                        self.style['fill'] = generateElementColor('d36b00')
                    elif 'background' in self.label['position']:
                        # bdb76b = darkkhaki
                        self.style['fill'] = generateElementColor('bdb76b')
                    elif 'dynamic' in self.label['position']:
                        # f08080 = lightcoral
                        self.style['fill'] = generateElementColor('e08080')
                    elif 'physics' in self.label['position']:
                        self.style['fill'] = generateElementColor('ee00ee')
                    else:
                        # 66cdaa = mediumaquamarine
                        self.style['fill'] = generateElementColor('66cdaa')
                else:
                    # 66cdaa = mediumaquamarine
                    self.style['fill'] = generateElementColor('66cdaa')

            if 'edge' in self.label:
                self.style['stroke-width'] = '1px'
                self.style['stroke-linecap'] = 'butt'
                self.style['stroke-linejoin'] = 'miter'
                self.style['stroke-opacity'] = '1'
                self.style['stroke'] = 'lime'

    def getoptions(self):
        """
            inkex loads the sys.argv in the default parameter of it
            getoptions method. for the unittests where the same extension is
            loaded multiple time with different parameters, it causes some
            problems because args keeps the old sys.argv values. as a
            consequence, we have to give it sys.argv as a parameter
        """
        Effect.getoptions(self, args=sys.argv[1:])
