from singleton import Singleton
from lxml import etree
from layer import Layer
from factory import Factory
from unit import UnitsConvertor
from inkex import addNS, NSS
from xmotoTools import createIfAbsent
from level import Level

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
                        if not dic.has_key(namespace):
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
        return self.lexer.next()

    def parse(self, pathInfoString):
        """ transform a string "M 123,123 L 213 345 L 43 54"
        into a sequence [("M", {'x':123, 'y':123}), ("L", {'':, '':}), ("C", ......]
        """
        def getOneValue():
            return float(self.getNextElement())

        def getPairOfValues():
            return (getOneValue(), getOneValue())

        def handle_M():
            x, y = getPairOfValues()
            # keep M coords. can be used in V and H
            self.x = x
            self.y = y
            return ('M', {'x' : x, 'y' : y})

        def handle_A():
            rx, ry          = getPairOfValues()
            x_axis_rotation = getOneValue()
            large_arc_flag  = getOneValue()
            sweep_flag      = getOneValue()
            x, y            = getPairOfValues()
            return ('A', {'rx' : rx, 'ry' : ry,
                    'x_axis_rotation' : x_axis_rotation,
                    'large_arc_flag'  : large_arc_flag,
                    'sweep_flag'      : sweep_flag,
                    'x' : x, 'y' : y})

        def handle_Q():
            x1, y1 = getPairOfValues()
            x,  y  = getPairOfValues()
            return ('Q', {'x1' : x1, 'y1' : y1,
                    'x' : x, 'y' : y})
                    
        def handle_T():
            x, y = getPairOfValues()
            return ('T', {'x' : x, 'y' : y})
        
        def handle_C():
            x1, y1 = getPairOfValues()
            x2, y2 = getPairOfValues()
            x, y   = getPairOfValues()
            return ('C', {'x1' : x1, 'y1' : y1,
                    'x2' : x2, 'y2' : y2,
                    'x'  : x,  'y'  : y})
        
        def handle_S():
            x2, y2 = getPairOfValues()
            x, y   = getPairOfValues()
            return ('S', {'x2' : x2, 'y2' : y2,
                    'x'  : x,  'y'  : y})
        
        def handle_L():
            x, y = getPairOfValues()
            return ('L', {'x' : x, 'y' : y})
        
        def handle_H():
            x = self.x
            y = getOneValue()
            return ('H', {'x' : x, 'y' : y})

        def handle_V():
            x = getOneValue()
            y = self.y
            return ('V', {'x' : x, 'y' : y})
        
        def handle_Z():
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
                  'Z' : handle_Z}

        self.parsedElements = []
        self.lexer = self.lexPath(pathInfoString)

        while True:
            try:
                curElement = self.getNextElement()
                curElement = curElement.upper()
                if switch.has_key(curElement):
                    self.parsedElements.append(switch[curElement.upper()]())
                else:
                    exc = "Unknown element in svg path: %s" % curElement
                    raise Exception(exc)
            except StopIteration:
                break

        return self.parsedElements

class XMLParser:
    __metaclass__ = Singleton

    def getNodeAttributes(self, node):
        """ returns them as a dic.
        key   = attribute name
        value = attribute value
        """
        return node.attrib

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
        attrs = self.getNodeAttributes(dom_svg)
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

        return Level(options, rootLayer)

    def scanLayers(self, dom_layer, matrix):
        """ there can be layers in svg... and each layer can have its
        own transformation """
        curLayer = Layer(self.getNodeAttributes(dom_layer), matrix)

        dom_paths = self.getChildren(dom_layer, 'path', 'svg')
        for dom_path in dom_paths:
            curLayer.addPath(self.getNodeAttributes(dom_path))

        dom_rects = self.getChildren(dom_layer, 'rect', 'svg')
        for dom_rect in dom_rects:
            curLayer.addRect(self.getNodeAttributes(dom_rect))

        dom_layerChildren = self.getChildren(dom_layer, 'g', 'svg')
        for dom_layerChild in dom_layerChildren:
            curLayer.addChild(self.scanLayers(dom_layerChild, curLayer.matrix))

        return curLayer

def initModule():
    Factory().registerObject('transform_parser', TransformParser)
    Factory().registerObject('XmlSvg_parser',    XMLParserSvg)
    Factory().registerObject('label_parser',     LabelParser)
    Factory().registerObject('path_parser',      PathParser)
    Factory().registerObject('style_parser',     StyleParser)

initModule()
