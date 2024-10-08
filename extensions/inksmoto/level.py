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

import logging
from datetime import date

from inksmoto.gui.bitmap import NOTSET_BITMAP
from .version  import Version
from .xmotoTools import getValue, delWoExcept
from .xmotoTools import NOTSET, createIfAbsent
from . import block_element, zone_element, entity_element
from .confGenerator import Conf
from .svgDoc import SvgDoc
from os.path import isdir, exists

class Level:
    def __init__(self, options, rootLayer, document):
        self.options = options
        self.rootLayer = rootLayer
        self.elements = []
        self.layersType = []
        self.layerBlock2Level = []
        self.content = []

        self.svg = SvgDoc(document)

        # the xmoto width of the level is the width of svg in pixel
        # divided by 20.0
        ratio = Conf()['SVG2LVL_RATIO']
        lvlWidth  = self.options['svg']['width']  * ratio
        lvlHeight = self.options['svg']['height'] * ratio

        createIfAbsent(self.options, 'lvl')
        self.options['lvl']['width'] = lvlWidth
        self.options['lvl']['height'] = lvlHeight
        self.options['lvl']['ratio'] = ratio

        self.limits = {}
        self.limits['left']   = -lvlWidth/2.0
        self.limits['right']  = lvlWidth/2.0
        self.limits['top']    = lvlHeight/2.0
        self.limits['bottom'] = -lvlHeight/2.0

        smooth = float(getValue(self.options, 'level', 'smooth', default='9'))
        # now, smooth is from 1 to 10 in the tkinter window,
        # but it is still from 1 to 100 in svg2lvl
        smooth += 90
        self.options['lvl']['smooth'] = smooth

        numLayers = len(self.rootLayer.children)
        self.createLayerInfos(numLayers)

        numLayers = 0
        self.rootLayer.elements = []
        for child in self.rootLayer.children:
            if (len(self.layersType) > 0
                and self.layersType[numLayers] != 'unused'):
                self.createEntitiesAndBlocksFromSvg(child, numLayers)
            else:
                child.unused = True
            numLayers += 1

        self.options['lvl']['rversion'] = self.getRequiredXmotoVersion()

    def createLayerInfos(self, numLayers):
        def putStaticLayers(numberLayer):
            self.layersType.append('static')
            self.layerBlock2Level.append(-1)
            if numberLayer == 2:
                self.layersType.append('2ndStatic')
                self.layerBlock2Level.append(-1)

        back = []
        front = []
        static = []
        unused = []

        useLayers = True
        if 'layer' not in self.options:
            if numLayers > 2:
                msg  = "The svg has more than two layers (the two main layers \
for the static blocks), but no layer informations has been put into the svg."
                raise Exception(msg)
            else:
                useLayers = False

        if useLayers == True:
            (self.options['layer'],
             dummy) = self.svg.updateLayerInfos(self.options['layer'])

            layer = 0
            isBack = True
            firstMain = True
            while True:
                if 'layer_%d_isused' % layer not in self.options['layer']:
                    break

                if self.options['layer']['layer_%d_isused' % layer] == 'false':
                    unused.append(layer)
                    self.layersType.append('unused')
                    self.layerBlock2Level.append(-1)
                elif self.options['layer']['layer_%d_ismain' % layer] == 'true':
                    static.append(layer)
                    self.layerBlock2Level.append(-1)
                    if firstMain == True:
                        self.layersType.append('static')
                        firstMain = False
                    else:
                        self.layersType.append('2ndStatic')
                    isBack = False
                else:
                    if isBack == True:
                        layerIdInLevel = len(back)
                        self.layerBlock2Level.append(layerIdInLevel)
                        back.append(layer)
                        self.layersType.append(layer)
                        key = 'layer_%d_isfront' % layer
                        self.options['layer'][key] = 'false'
                    else:
                        layerIdInLevel = len(back)+len(front)
                        self.layerBlock2Level.append(layerIdInLevel)
                        front.append(layer)
                        self.layersType.append(layer)
                        key = 'layer_%d_isfront' % layer
                        self.options['layer'][key] = 'true'
                layer += 1

            if layer != numLayers:
                raise Exception("You added layers to your level without \
setting their properties in the layer properties window.")

        else:
            if numLayers in [1, 2]:
                putStaticLayers(numLayers)
                return

        if len(static) > 0:
            numStatic = len(static)
        else:
            numStatic = numLayers - (len(front) + len(back) + len(unused))

        logging.info("numlayer=[%d] static=[%d]" % (numLayers, len(static)))
        logging.info("front=[%d]" % len(front))
        logging.info("back=[%d]" % len(back))
        logging.info("unused=[%d]" % len(unused))

        if numStatic not in [1, 2]:
            if (len(static) == 0 and len(front) == 0 and len(unused) == 0
                and len(back) == numLayers and numLayers in [1, 2]):
                # the user opened the layer properties window and
                # press 'OK' without putting the main layers
                putStaticLayers(numLayers)
                return
            if numStatic <= 0:
                msg =  "Error, you have put too many layers in the layer \
properties window or you have put no main layer.\nThere must be one or two \
main layers (the main level)."
                raise Exception(msg)
            else:
                msg = "Error, there's %d layers in the svg. %d back layers, \
%d front layers.\nSo, even if there's 2 static layers, there's still %d layers \
with no properties." % (numLayers, len(back), len(front), numStatic-2)
                raise Exception(msg)

        logging.info("layerInfos=%s" % str(self.layersType))

    def generateLvlContent(self, lvlfile):
        self.writeLevelHead()
        if getValue(self.options, 'level', 'lua') not in NOTSET:
            self.writeLevelScript(self.options['level']['lua'])
        self.writeLevelContent(self.rootLayer)
        self.content.append("</level>")

        if lvlfile == None:
            self.printContentToStdout()
        else:
            lvlfile.writelines([(line+'\n').encode("utf-8")
                                for line in self.content])
            lvlfile.close()

    def printContentToStdout(self):
        """ print the lvl on stdout so inkscape gets it """
        for line in self.content:
            print(line.encode("utf-8"))

    def writeLevelScript(self, scriptName):
        if isdir(scriptName) or not exists(scriptName):
            logging.warning("writeLevelScript::the script [%s] is a directory \
or doesn't exist." % scriptName)
            return

        f = open(scriptName)
        lines = f.readlines()
        f.close()

        script = []

        script.append("\t<script>")
        script.extend([l.replace('<', '&lt;').replace('>', '&gt;').rstrip('\n')
                       for l in lines])
        script.append("\t</script>")

        self.content.extend(script)

    def writeLevelContent(self, layer):
        if layer.unused == True:
            return

        for child in layer.children:
            self.writeLevelContent(child)

        for el in layer.elements:
            self.content.extend(el.writeContent(self.options['lvl'], self))

    def createEntitiesAndBlocksFromSvg(self, layer, numLayers):
        # there's been a svg with path without 'd' which causes an exception
        layer.elements = [path.createElement(numLayers)
                          for path in layer.paths
                          if 'd' in path.attrs]

        for child in layer.children:
            self.createEntitiesAndBlocksFromSvg(child, numLayers)

    def writeLevelHead(self):
        head = []

        _id = getValue(self.options, 'level', 'id', default='defaultId')
        rversion = self.options['lvl']['rversion']
        name = getValue(self.options, 'level', 'name', default='defaultName')
        desc = getValue(self.options, 'level', 'desc', default='')
        author = getValue(self.options, 'level', 'author', default='')
        today = str(date.today())

        if _id == '':
            _id = 'defaultId'
        if name == '':
            name = 'defaultName'

        head.append("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        head.append("<level id=\"%s\" rversion=\"%s\">" % (_id, rversion))
        head.append("\t<info>")
        head.append("\t\t<name>%s</name>" % name)
        head.append("\t\t<description>%s</description>" % desc)
        head.append("\t\t<author>%s</author>" % author)
        head.append("\t\t<date>%s</date>" % today)

        # sky
        sky = "\t\t<sky"
        if 'sky' in self.options:
            # drifted is useless when it's put to false
            drifted = getValue(self.options, 'sky', 'drifted', default='false')
            if drifted == 'false':
                delWoExcept(self.options['sky'], 'drifted')

            tex = getValue(self.options, 'sky', 'tex')
            if tex in NOTSET_BITMAP:
                tex = ''
            delWoExcept(self.options['sky'], 'tex')

            for skyParam, value in self.options['sky'].items():
                if not skyParam.startswith('_') and value != '':
                    sky += ' %s="%s"' % (skyParam, value)

            sky += ">%s</sky>" % tex
            head.append(sky)
        else:
            sky += ">%s</sky>" % 'sky1'
            head.append(sky)

        # border
        border = getValue(self.options, 'level', 'tex')
        if border not in NOTSET_BITMAP:
            head.append("\t\t<border texture=\"%s\"/>" % border)

        # music
        music = getValue(self.options, 'level', 'music')
        if music not in NOTSET:
            head.append("\t\t<music name=\"%s\" />" % music)

        head.append("\t</info>")

        # remplacement
        if 'remplacement' in self.options:
            # we want to add to the level the <theme_replacements>
            # tags only if there's some theme replacements.
            first = True

            line = "\t\t<sprite_replacement old_name=\"%s\" new_name=\"%s\"/>"
            for key, value in self.options['remplacement'].items():
                if (value not in NOTSET
                    and key.find('Scale') == -1
                    and key != value):
                    if first == True:
                        head.append("\t<theme_replacements>")
                        first = False
                    head.append(line % (key, value))
            if first == False:
                head.append("\t</theme_replacements>")

        # layer
        if 'layer' in self.options:
            # only add the <layeroffsets> tag if there's really some layers
            first = True
            line = "\t\t<layeroffset x=\"%s\" y=\"%s\" frontlayer=\"%s\"/>"
            layerInfos = self.options['layer']
            for _id in self.layersType:
                if _id in ['static', '2ndStatic', 'unused']:
                    continue
                if first == True:
                    head.append("\t<layeroffsets>")
                    first = False
                head.append(line % (layerInfos['layer_%d_x' % _id],
                                    layerInfos['layer_%d_y' % _id],
                                    layerInfos['layer_%d_isfront' % _id]))
            if first == False:
                head.append("\t</layeroffsets>")

        # limits
        head.append("\t<limits left=\"%f\" right=\"%f\" \
top=\"%f\" bottom=\"%f\"/>" % (self.limits['left'], self.limits['right'],
                               self.limits['top'],  self.limits['bottom']))

        self.content.extend(head)

    def getRequiredXmotoVersion(self):
        return "%d.%d.%d" % Version().minVersion(self.options, self.rootLayer)

    def getLayersType(self):
        return self.layersType

    def getLayerBlock2Level(self):
        return self.layerBlock2Level
