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
from singleton import Singleton
from lxml import etree
from layer import Layer
from factory import Factory
from unit import UnitsConvertor
from inkex import addNS, NSS
from xmotoTools import createIfAbsent
from level import Level
from svgnode import convertToXmNode, XmNode
from simplepath import parsePath

class TransformParser:
    __metaclass__ = Singleton

    def lexTransform(self, transform):
        import re

        offset = 0
        length = len(transform)
        delim = r'[(), ]+'
        delim = re.compile(delim)
        command = r'[a-zA-Z]+'
        command = re.compile(command)
        param = r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)'
        param = re.compile(param)

        while True:
            m = delim.match(transform, offset)
            if m:
                offset = m.end()
            if offset >= length:
                break
            m = command.match(transform, offset)
            if m:
                yield ('cmd', transform[offset:m.end()])
                offset = m.end()
                continue
            m = param.match(transform, offset)
            if m:
                yield ('param', transform[offset:m.end()])
                offset = m.end()
                continue
            raise Exception, 'Invalid transform data!'

    def parse(self, inData):
        """ input: 'translate(234.43,54545.65) skewX(43.43) ...'
            output: ['translate', 2, 234.43, 54545.65, 'skewX', 1, 43.43, ...]
        """
        result = []
        if inData == '':
            return result
        self.lexer = self.lexTransform(inData)
        self.curCmd = None
        self.curParams = []
        while True:
            try:
                (type, value) = self.lexer.next()
                if type == 'cmd':
                    if self.curCmd is None:
                        self.curCmd = value
                    else:
                        result.extend([self.curCmd, len(self.curParams)])
                        result.extend(self.curParams)

                        self.curCmd = value
                        self.curParams = []
                else:
                    self.curParams.append(float(value))
                
            except StopIteration:
                result.extend([self.curCmd, len(self.curParams)])
                result.extend(self.curParams)
                break

        return result

    def unparse(self, inData):
        """ input: ['translate', 2, 234.43, 54545.65, 'skewX', 1, 43.43, ...]
            output: 'translate(234.43,54545.65) skewX(43.43) ...'
        """
        result = ''

        while len(inData) > 0:
            result += str(inData.pop(0)) + '('
            nbParam   = inData.pop(0)
            # there's at least one parameter
            for i in xrange(nbParam-1):
                result += str(inData.pop(0)) + ','
            result += str(inData.pop(0))
             
            result += ') '

        if result[-1] == ' ':
            result = result[:-1]

        return result

class LabelParser:
    __metaclass__ = Singleton

    def parse(self, label):
        """ label must be with the form:
        type5=val5|namespace1:type1=val1|namespace2:type2=val2|namespace2:type3|namespace3:type4=val4
        and the output is a dic:
        {type5:val5, namespace1:{'type1':val1}, namespace2:{'type2':val2, 'type3':''}, namespace3:{'type4':'val4'}}        
        """
        dic = {}
        if label is not None:
            infos = [info.strip() for info in label.split('|')]

            for info in infos:
                if info != '':
                    infoSplit = info.split('=')
                    name  = infoSplit[0]
                    value = '='.join(infoSplit[1:])
                    if name.find(':') != -1:
                        namespace, name = name.split(':')
                        if namespace not in dic:
                            dic[namespace] = {}
                        dic[namespace][name] = value
                    else:
                        dic[name] = value

        return dic

    def unparse(self, dic):
        result = []
        for (name, value) in dic.iteritems():
            if type(value) == dict:
                namespace    = name
                namespaceDic = value
                for (name, value) in namespaceDic.iteritems():
                    result.append("%s:%s=%s" % (namespace, name, value))
            else:
                result.append("%s=%s" % (name, value))

        return '|'.join(result)

def parse(data, elementSep, keyValueSep):
    dic = {}
    infos = [info.strip() for info in data.split(elementSep)]
    
    for info in infos:
        if info != '':
            infoSplit = info.split(keyValueSep)
            dic[infoSplit[0]] = keyValueSep.join(infoSplit[1:])
        
    return dic

def unparse(dic, elementSep, keyValueSep):
    return elementSep.join([keyValueSep.join([str(value)
                                              for value in param
                                              if value != None])
                            for param in dic.items()])

class StyleParser:
    __metaclass__ = Singleton
    
    def parse(self, style):
        """ style is in the form:
            key:value;key:value
            output is a dic:
            {'key': value, 'key': value'}
        """
        return parse(style, ';', ':')

    def unparse(self, dic):
        return unparse(dic, ';', ':')

class PathParser:
    __metaclass__ = Singleton

    def parse(self, d):
        """ transform a string "M 123,123 L 213 345 L 43 54"
        into a sequence [("M", {'x':123, 'y':123}), ("L", {'':, '':}), ("L", ......]
        """
        parsedPath = parsePath(d)

        parsedPaths = []
        # cut paths
        lastIdx = 0
        for idx in xrange(len(parsedPath)):
            if parsedPath[idx][0] == 'Z':
                parsedPaths.append(parsedPath[lastIdx:idx])
                lastIdx = idx+1
        # if there's no z at the end:
        if lastIdx < len(parsedPath):
            parsedPaths.append(parsedPath[lastIdx:])

        return parsedPaths

class XMLParser:
    __metaclass__ = Singleton

    def getChildren(self, node, childName, childNS=''):
        """ returns them as a list
        """
        children = []

        if childNS != '':
            childName = addNS(childName, childNS)

        for child in node:
            if child.tag == childName:
                children.append(child)

        return children

    def getNodeText(self, node):
        return node.text

class XMLParserSvg(XMLParser):
    def parse(self, svgFile):
        document = etree.parse(svgFile)

        # there is a main svg node in a svg file
        dom_svg = document.getroot()

        # the main svg node has width and height attributes
        attrs = dom_svg.attrib
        width  = UnitsConvertor(attrs['width']).convert('px')
        height = UnitsConvertor(attrs['height']).convert('px')

        levelOptions = dom_svg.xpath('//dc:description', namespaces=NSS)
        if levelOptions is not None and len(levelOptions) > 0:
            description = self.getNodeText(levelOptions[0])
        else:
            description = None

        labelParser = Factory().create('label_parser')
        options = labelParser.parse(description)
        createIfAbsent(options, 'svg')
        options['svg']['width']  = width
        options['svg']['height'] = height

        rootLayer = self.scanLayers(dom_svg, None)

        return Level(options, rootLayer, document)

    def scanLayers(self, dom_layer, matrix):
        """ there can be layers in svg... and each layer can have its
        own transformation """
        curLayer = Layer(dom_layer.attrib, matrix)

        dom_paths = self.getChildren(dom_layer, 'path', 'svg')
        for dom_path in dom_paths:
            curLayer.addPath(dom_path.attrib)

        dom_rects = self.getChildren(dom_layer, 'rect', 'svg')
        for dom_rect in dom_rects:
            curLayer.addRect(dom_rect.attrib)

        dom_layerChildren = self.getChildren(dom_layer, 'g', 'svg')
        for dom_layerChild in dom_layerChildren:
            if dom_layerChild.get(addNS('xmoto_label', 'xmoto')) is None:
                curLayer.addChild(self.scanLayers(dom_layerChild, curLayer.matrix))
            else:
                dom_layerChild = convertToXmNode(dom_layerChild)
                if dom_layerChild.isSubLayer(type=XmNode.BITMAP) == True:
                    # add the circle
                    circle = dom_layerChild.getCircleChild()
                    # copy the transform attr from the sublayer to the circle
                    transform = dom_layerChild.get('transform', default='')
                    if transform != '':
                        circle.set('transform', transform)
                    curLayer.add(circle)
                elif dom_layerChild.isSubLayer(type=XmNode.BLOCK) == True:
                    # add one of the two children
                    #curLayer.add(list(dom_layerChild)[0])
                    pass
                else:
                    raise Exception("The node %s.%s is a sublayer but \
is neither a colored block nor a bitmap." % (dom_layerChild.tag,
                                             dom_layerChild.get('id', '')))

        return curLayer

def initModule():
    Factory().register('transform_parser', TransformParser)
    Factory().register('XmlSvg_parser', XMLParserSvg)
    Factory().register('label_parser', LabelParser)
    Factory().register('path_parser', PathParser)
    Factory().register('style_parser', StyleParser)

initModule()
