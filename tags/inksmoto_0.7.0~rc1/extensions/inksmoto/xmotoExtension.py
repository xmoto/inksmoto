#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import log, logging
import sys, random
from inkex import Effect, NSS, addNS
from parsers import LabelParser, StyleParser
from xmotoTools import createIfAbsent, applyOnElements, getBoolValue
from xmotoTools import getValue, dec2hex, hex2dec, updateInfos, color2Hex
from svgnode import XmNode, convertToXmNode
from factory import Factory
from svgDoc import SvgDoc
from testsCreator import TestsCreator

from confGenerator import Conf
ENTITY_RADIUS = Conf()['ENTITY_RADIUS']
SVG2LVL_RATIO = Conf()['SVG2LVL_RATIO']

from availableElements import AvailableElements
TEXTURES = AvailableElements()['TEXTURES']
SPRITES = AvailableElements()['SPRITES']
PARTICLESOURCES = AvailableElements()['PARTICLESOURCES']

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
        self.svg = SvgDoc()
        # always the same seed to always generate the same random numbers
        # so that generated unittests works
        random.seed(1234567890)

    def handlePath(self, node):
        label = XmNode(node).getParsedLabel()

        label = self.getNewLabel(label)
        style = self.generateStyle(label)

        self.updateNodeSvgAttributes(node, label, style)

    def effect(self):
        self.svg.setDoc(self.document)

        # some extensions may need to not only manipulate the selected
        # objects in the svg (like adding new elements)
        if self.effectHook() == True:
            applyOnElements(self, self.selected, self.handlePath)

    # the two methods to implement in children
    def effectHook(self):
        return True

    def getNewLabel(self, label):
        return label

    def updateNodeSvgAttributes(self, node, label, style):
        node = convertToXmNode(node, self.svg)
        labelValue = LabelParser().unparse(label)
        styleValue = StyleParser().unparse(style)

        # if the user select the an element in the sublayer using the
        # 'circle tool' for example, the selected node will be that
        # element, not the sublayer (the sublayer is selected when you
        # use the 'selection tool').
        # in this case, use the sublayer instead of the selected child
        if node.belongsToSubLayer() == True:
            node = convertToXmNode(node.getparent())

        # update node shape
        # ugly and clumsy but will be refactored with xmObjects later
        if 'typeid' in label:
            # entity or zone
            typeid = label['typeid']

            if typeid in ['PlayerStart', 'EndOfLevel', 'Strawberry', 'Wrecker']:
                if typeid == 'EndOfLevel':
                    typeid = 'Flower'

                metadata = self.svg.getMetaDataValue()
                metadata = LabelParser().parse(metadata)

                texName = getValue(metadata, 'remplacement',
                                   typeid, default=typeid)
                scale = float(getValue(metadata, 'remplacement',
                                       typeid+'Scale', 1.0))
                _reversed = getBoolValue(label, 'position', 'reversed')
                rotation = float(getValue(label, 'position',
                                          'angle', 0.0))
                radius = ENTITY_RADIUS[typeid] / SVG2LVL_RATIO

                node.setNodeAsBitmap(self.svg, texName, radius, SPRITES,
                                     labelValue, styleValue, scale,
                                     _reversed, rotation)

            elif typeid == 'ParticleSource':
                texName  = getValue(label, 'param', 'type', '')
                radius   = ENTITY_RADIUS[typeid] / SVG2LVL_RATIO

                node.setNodeAsBitmap(self.svg, texName, radius,
                                     PARTICLESOURCES, labelValue, styleValue)

            elif typeid == 'Sprite':
                texName = getValue(label, 'param', 'name', '')
                scale = float(getValue(label, 'size', 'scale', 1.0))
                _reversed = getBoolValue(label, 'position', 'reversed')
                rotation = float(getValue(label, 'position',
                                               'angle', 0.0))
                radius   = ENTITY_RADIUS['Sprite'] / SVG2LVL_RATIO

                node.setNodeAsBitmap(self.svg, texName, radius,
                                     SPRITES, labelValue, styleValue,
                                     scale, _reversed, rotation)

            elif typeid == 'Zone':
                (node, aabb) = node.subLayerElementToSingleNode()
                node.setNodeAsRectangle(aabb)
                # we may have set the label and still to a child of
                # 'g', and now node is the 'g', so we have to set it
                # to it too.
                node.setStyleLabel(labelValue, styleValue)

            elif typeid == 'Joint':
                # the addJoint extension already create the joints
                # with the right shape
                pass

            else:
                raise Exception("typeid=%s not handled by \
updateNodeSvgAttributes" % typeid)

        else:
            # block
            if node.isSubLayer(type=XmNode.BITMAP) == True:
                log.outMsg("Can't convert an entity to a block")
                return
#            elif (getValue(label, 'usetexture', 'color_r', 255) != 255
#                or getValue(label, 'usetexture', 'color_g', 255) != 255
#                or getValue(label, 'usetexture', 'color_b', 255) != 255):
#                # a color is not 255, we have to set two blocks, one
#                # textured and one colored
#                coloredStyle = self.generateStyle(label, coloredBlock=True)
#                coloredStyleValue = StyleParser().unparse(coloredStyle)
#
#                g = node.getSubLayerNode()
#                g.addColoredChildren(node, labelValue, styleValue, coloredStyleValue)
            else:
                if node.isSubLayer(type=XmNode.BLOCK) == True:
                    # remove sublayer and colored block
                    node.removeColoredChildren(labelValue, styleValue)
                else:
                    # nothing to do
                    pass

        node.setStyleLabel(labelValue, styleValue)

    def generateStyle(self, label, coloredBlock=False):
        def generateElementColor(color):
            """ randomly change the color to distinguish between
            adjacent elements """
            from random import randint
            # r, g and b must not be 'f' before adding the random int
            # or it could became '0'
            r = (hex2dec(color[0]) + randint(0, 1)) % 16
            g = (hex2dec(color[2]) + randint(0, 1)) % 16
            b = (hex2dec(color[4]) + randint(0, 1)) % 16
            return ('#' + dec2hex(r) + color[1]
                    + dec2hex(g) + color[3]
                    + dec2hex(b) + color[5])

        style = {}
        if 'typeid' in label:
            # entity or zone
            typeid = label['typeid']

            if typeid in ['PlayerStart', 'EndOfLevel', 'ParticleSource',
                          'Sprite', 'Strawberry', 'Wrecker']:
                style['fill'] = 'none'
                style['stroke-width'] = '1px'
                style['stroke-linecap'] = 'butt'
                style['stroke-linejoin'] = 'miter'
                style['stroke-opacity'] = '1'

            if typeid == 'PlayerStart':
                # blue
                style['stroke'] = generateElementColor('0000ee')
            elif typeid == 'EndOfLevel':
                # yellow
                style['stroke'] = generateElementColor('eeee00')
            elif typeid == 'ParticleSource':
                # orange
                style['stroke'] = generateElementColor('eea500')
            elif typeid == 'Sprite':
                # purple
                style['stroke'] = generateElementColor('800080')
            elif typeid == 'Strawberry':
                # red
                style['stroke'] = generateElementColor('ee0000')
            elif typeid == 'Wrecker':
                # gray
                style['stroke'] = generateElementColor('808080')
            elif typeid == 'Zone':
                # cyan
                style['fill'] = generateElementColor('00eeee')
                style['fill-opacity'] = 0.5
            elif typeid == 'Joint':
                # green
                style['fill'] = generateElementColor('00ee00')
                if getValue(label, 'joint', 'type', '') == 'pin':
                    style['stroke'] = '#000000'
                    style['stroke-opacity'] = '1'
            else:
                # black
                style['fill'] = generateElementColor('000000')
        else:
            # block
            if coloredBlock == False:
                createIfAbsent(label, 'usetexture')
                if 'id' not in label['usetexture']:
                    label['usetexture']['id'] = 'Dirt'

                # display the texture, if the texture is missing, display
                # the old colors
                try:
                    scale = float(getValue(label, 'usetexture', 'scale', 1.0))
                    patternId = self.svg.addPattern(label['usetexture']['id'],
                                                    TEXTURES, scale)
                    style['fill'] = 'url(#%s)' % patternId
                except Exception, e:
                    logging.info("Can't create pattern for texture %s.\n%s"
                                 % (label['usetexture']['id'], e))
                    style['fill-opacity'] = '1'
                    if 'position' in label:
                        if ('background' in label['position']
                            and 'dynamic' in label['position']):
                            # d36b00
                            style['fill'] = generateElementColor('d36b00')
                        elif 'background' in label['position']:
                            # bdb76b = darkkhaki
                            style['fill'] = generateElementColor('bdb76b')
                        elif 'dynamic' in label['position']:
                            # f08080 = lightcoral
                            style['fill'] = generateElementColor('e08080')
                        elif 'physics' in label['position']:
                            style['fill'] = generateElementColor('ee00ee')
                        else:
                            # 66cdaa = mediumaquamarine
                            style['fill'] = generateElementColor('66cdaa')
                    else:
                        # 66cdaa = mediumaquamarine
                        style['fill'] = generateElementColor('66cdaa')
            else:
                r = getValue(label, 'usetexture', 'color_r', default=255)
                g = getValue(label, 'usetexture', 'color_g', default=255)
                b = getValue(label, 'usetexture', 'color_b', default=255)
                style['fill'] = color2Hex(r, g, b)

            # mix in the color (alpha for the moment)
            alpha = float(getValue(label, 'usetexture', 'color_a', 255)) / 255.0
            if alpha != 1.0:
                style['opacity'] = alpha

            if 'edge' in label:
                style['stroke-width'] = '1px'
                style['stroke-linecap'] = 'butt'
                style['stroke-linejoin'] = 'miter'
                style['stroke-opacity'] = '1'
                (useGradient, gradientId) = self.svg.addGradient(label)
                if useGradient == True:
                    style['stroke'] = 'url(#%s)' % gradientId
                else:
                    style['stroke'] = 'lime'

        return style

    def getoptions(self):
        """
            inkex loads the sys.argv in the default parameter of it
            getoptions method. for the unittests where the same extension is
            loaded multiple time with different parameters, it causes some
            problems because args keeps the old sys.argv values. as a
            consequence, we have to give it sys.argv as a parameter
        """
        Effect.getoptions(self, args=sys.argv[1:])

    def parse(self):
        file = self.args[-1]
        Effect.parse(self, file)

        # we don't want to record the output of the enableTrace extension
        self.recording = False
        if Conf()['enableRecording'] == True:
            # create in svg file
            TestsCreator().addInSvg(file)
            TestsCreator().addTestArgvModule(self.options, self)
            self.recording = True

    def output(self):
        Effect.output(self)

        if self.recording == True and Conf()['enableRecording'] == True:
            testsCreator = TestsCreator()
            # create out svg file
            testsCreator.addOutSvg(self.document)

            testsCreator.writeTestValues()

            # increment test number
            conf = Conf()
            conf['currentTest'] += 1
            conf.write()
