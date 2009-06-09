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

from singleton import Singleton
from lxml import etree
from layer import Layer
from factory import Factory
from unit import UnitsConvertor
from inkex import addNS, NSS
from xmotoTools import createIfAbsent
from level import Level
from svgnode import convertToXmNode, XmNode

class TransformParser:
    __metaclass__ = Singleton

    def parse(self, inData):
        """ input: 'translate(234.43,54545.65) skewX(43.43) ...'
            output: ['translate', 2, 234.43, 54545.65, 'skewX', 1, 43.43, ...]
        """
        result = []

        transforms = inData.split(' ')
        for transform in transforms:
            posParenthese = transform.find('(')

            if posParenthese == -1:
                break

            transformName = transform[:posParenthese]
            result.append(transformName)

            numberArg = transform.count(',', posParenthese) + 1
            result.append(numberArg)

            inf = posParenthese + 1
            for i in xrange(numberArg):
                sup = transform.find(',', inf)
                result.append(float(transform[inf:sup]))
                inf = sup + 1                              

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

    def lexPath(self, d):
        """
        From simplepath.py by Aaron Spike
        returns and iterator that breaks path data 
        """
        import re

        offset = 0
        length = len(d)
        delim = r'[ \t\r\n,]+'
        delim = re.compile(delim)
        command = r'[MLHVCSQTAZmlhvcsqtaz]'
        command = re.compile(command)
        param = r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)'
        param = re.compile(param)
        while 1:
            m = delim.match(d, offset)
            if m:
                offset = m.end()
            if offset >= length:
                break
            m = command.match(d, offset)
            if m:
                yield d[offset:m.end()]
                offset = m.end()
                continue
            m = param.match(d, offset)
            if m:
                yield d[offset:m.end()]
                offset = m.end()
                continue
            raise Exception, 'Invalid path data!'

    def getNextElement(self):
        if self.savedParam is not None:
            ret = self.savedParam
            self.savedParam = None
            return ret
        else:
            return self.lexer.next()

    def parse(self, pathInfoString):
        """ transform a string "M 123,123 L 213 345 L 43 54"
        into a sequence [("M", {'x':123, 'y':123}), ("L", {'':, '':}), ("C", ......]
        """
        def getOneValue():
            return float(self.getNextElement())

        def getPairOfValues():
            return (getOneValue(), getOneValue())

        def handle_M(relative=False):
            x, y = getPairOfValues()
            # keep M coords. can be used in V and H
            if relative == True:
                x += self.x
                y += self.y
            self.x = x
            self.y = y
            return ('M', {'x' : x, 'y' : y})

        def handle_A(relative=False):
            rx, ry          = getPairOfValues()
            x_axis_rotation = getOneValue()
            large_arc_flag  = getOneValue()
            sweep_flag      = getOneValue()
            x, y            = getPairOfValues()
            if relative == True:
                x += self.x
                y += self.y
            return ('A', {'rx' : rx, 'ry' : ry,
                    'x_axis_rotation' : x_axis_rotation,
                    'large_arc_flag'  : large_arc_flag,
                    'sweep_flag'      : sweep_flag,
                    'x' : x, 'y' : y})

        def handle_Q(relative=False):
            x1, y1 = getPairOfValues()
            x,  y  = getPairOfValues()
            if relative == True:
                x += self.x
                y += self.y
                x1 += self.x
                y1 += self.y
            return ('Q', {'x1' : x1, 'y1' : y1,
                    'x' : x, 'y' : y})
                    
        def handle_T(relative=False):
            x, y = getPairOfValues()
            if relative == True:
                x += self.x
                y += self.y
            return ('T', {'x' : x, 'y' : y})
        
        def handle_C(relative=False):
            x1, y1 = getPairOfValues()
            x2, y2 = getPairOfValues()
            x, y   = getPairOfValues()
            if relative == True:
                x += self.x
                y += self.y
                x1 += self.x
                y1 += self.y
                x2 += self.x
                y2 += self.y
            return ('C', {'x1' : x1, 'y1' : y1,
                    'x2' : x2, 'y2' : y2,
                    'x'  : x,  'y'  : y})
        
        def handle_S(relative=False):
            x2, y2 = getPairOfValues()
            x, y   = getPairOfValues()
            if relative == True:
                x += self.x
                y += self.y
                x2 += self.x
                y2 += self.y
            return ('S', {'x2' : x2, 'y2' : y2,
                    'x'  : x,  'y'  : y})
        
        def handle_L(relative=False):
            x, y = getPairOfValues()
            if relative == True:
                x += self.x
                y += self.y
            return ('L', {'x' : x, 'y' : y})
        
        def handle_H(relative=False):
            x = self.x
            y = getOneValue()
            if relative == True:
                y += self.y
            return ('H', {'x' : x, 'y' : y})

        def handle_V(relative=False):
            x = getOneValue()
            y = self.y
            if relative == True:
                x += self.x
            return ('V', {'x' : x, 'y' : y})
        
        def handle_Z(relative=False):
            return ('Z', None)
        
        switch = {'M' : handle_M,
                  'A' : handle_A,
                  'Q' : handle_Q,
                  'T' : handle_T,
                  'C' : handle_C,
                  'S' : handle_S,
                  'L' : handle_L,
                  'H' : handle_H,
                  'V' : handle_V,
                  'Z' : handle_Z,
                  'm' : lambda : handle_M(True),
                  'a' : lambda : handle_A(True),
                  'q' : lambda : handle_Q(True),
                  't' : lambda : handle_T(True),
                  'c' : lambda : handle_C(True),
                  's' : lambda : handle_S(True),
                  'l' : lambda : handle_L(True),
                  'h' : lambda : handle_H(True),
                  'v' : lambda : handle_V(True),
                  'z' : lambda : handle_Z(True)}

        self.parsedElements = []
        self.lexer = self.lexPath(pathInfoString)

        self.savedParam = None
        previousElement = None
        (self.x, self.y) = (0.0, 0.0)
        while True:
            try:
                curElement = self.getNextElement()
                if curElement in switch:
                    self.parsedElements.append(switch[curElement]())
                elif previousElement is not None:
                    self.savedParam = curElement
                    curElement = previousElement
                    self.parsedElements.append(switch[curElement]())
                else:
                    exc = "Unknown element in svg path: %s" % curElement
                    raise Exception(exc)

                previousElement = curElement
            except StopIteration:
                break

        return self.parsedElements

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

        labelParser = Factory().createObject('label_parser')
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
                    curLayer.add(circle)
                elif dom_layerChild.isSubLayer(type=XmNode.BLOCK) == True:
                    # add one of the two children
                    curLayer.add(list(dom_layerChild)[0])
                else:
                    raise Exception("The node %s.%s is a sublayer but \
is neither a colored block nor a bitmap." % (dom_layerChild.tag,
                                             dom_layerChild.get('id', '')))

        return curLayer

def initModule():
    Factory().registerObject('transform_parser', TransformParser)
    Factory().registerObject('XmlSvg_parser',    XMLParserSvg)
    Factory().registerObject('label_parser',     LabelParser)
    Factory().registerObject('path_parser',      PathParser)
    Factory().registerObject('style_parser',     StyleParser)

initModule()