from singleton       import Singleton
from xml.dom.minidom import parse
from layer           import Layer
from factory         import Factory
import logging, log

class TransformParser:
    __metaclass__ = Singleton

    def parse(self, inData):
        """ input: 'translate(234.43,54545.65) skewX(43.43) ...'
            output: ['translate', '234.43', '54545.65', 'skewX', '43.43', ...]
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
                
        logging.debug("TransformParser::transforms: %s -> %s"
                      % (str(transforms), str(result)))
        
        return result


class LabelParser:
    __metaclass__ = Singleton

    def parse(self, label):
        """ label must be with the form:
        type1=val1|type2=val2|type3|type4=val4
        and the output is a dic:
        {'type1':val1, 'type2':val2, 'type3':'', 'type4':'val4'}        
        """
        dic = {}
        infos = [info.strip() for info in label.split('|')]
        
        for info in infos:
            if info != '':
                infoSplit = info.split('=')
                dic[infoSplit[0]] = '='.join(infoSplit[1:])
            
        return dic

    def unparse(self, dic):
        return '|'.join(['='.join([str(value) for value in param if value != None]) for param in dic.items()])

class PathParser:
    __metaclass__ = Singleton

    def parse(self, pathInfoString):
        """ transform a string "M 123,123 L 213 345 L 43 54"
        into a sequence [("M", {'x':123, 'y':123}), ("L", {'':, '':}), ("C", ......]
        it assumes that there is a space between letters and numbers (svg doesn't garanty this)
        FIXME::use regexp to loop through data only once
        """
        def getValuesInCoords(coords, pos):
            return float(coords[:pos]), float(coords[pos+1:])

        def isElementACoord(coords):
            """ -1:    False
                other: True
            """
            return coords.find(',')

        def getPairOfValues():
            element = self.elements.pop(0)
            pos     = isElementACoord(element)
            if pos == -1:
                x = float(element)
                y = getOneValue()
            else:
                x, y = getValuesInCoords(element, pos)
            return x, y
        
        def getOneValue():
            return float(self.elements.pop(0))

        def handle_M():
            x, y = getPairOfValues()
            # keep M coords. can be used in V and H
            self.x = x
            self.y = y
            return {'x' : x, 'y' : y}

        def handle_A():
            rx, ry          = getPairOfValues()
            x_axis_rotation = getOneValue()
            large_arc_flag  = getOneValue()
            sweep_flag      = getOneValue()
            x, y            = getPairOfValues()
            return {'rx' : rx, 'ry' : ry,
                    'x_axis_rotation' : x_axis_rotation,
                    'large_arc_flag'  : large_arc_flag,
                    'sweep_flag'      : sweep_flag,
                    'x' : x, 'y' : y}
        
        def handle_Q():
            x1, y1 = getPairOfValues()
            x,  y  = getPairOfValues()
            return {'x1' : x1, 'y1' : y1,
                    'x' : x, 'y' : y}
                    
        def handle_T():
            x, y = getPairOfValues()
            return {'x' : x, 'y' : y}
        
        def handle_C():
            x1, y1 = getPairOfValues()
            x2, y2 = getPairOfValues()
            x, y   = getPairOfValues()
            return {'x1' : x1, 'y1' : y1,
                    'x2' : x2, 'y2' : y2,
                    'x'  : x,  'y'  : y}
        
        def handle_S():
            x2, y2 = getPairOfValues()
            x, y   = getPairOfValues()
            return {'x2' : x2, 'y2' : y2,
                    'x'  : x,  'y'  : y}
        
        def handle_L():
            x, y = getPairOfValues()
            return {'x' : x, 'y' : y}
        
        def handle_H():
            x = getOneValue()
            y = self.y
            return {'x' : x, 'y' : y}

        def handle_V():
            x = getOneValue()
            y = self.y
            return {'x' : x, 'y' : y}
        
        def handle_Z():
            return None
        
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
        
        self.elements = [element for element in pathInfoString.strip().split(' ') if element != '']
        
        while len(self.elements) > 0:
            curElement = self.elements.pop(0)
            curElement = curElement.upper()
            if switch.has_key(curElement):
                self.parsedElements.append((curElement, switch[curElement.upper()]()))
            else:
                raise Exception("Unknown element in svg path: %s" % curElement)

        return self.parsedElements

class XMLParser:
    __metaclass__ = Singleton
    def __init__(self):
        pass

    def extractFloatFromString(self, s):
        import re
        p = re.compile('[-+]?(\d+(\.\d*)?|\d*\.\d+)([eE][-+]?\d+)?')
        m = p.match(s)
        return m.group()

    def parse(self, svgName, level):
        svgfile = open(svgName, 'r')
            
        dom = parse(svgfile)

        # there is a main svg node in a svg file
        dom_svg = dom.getElementsByTagName("svg")[0]

        # the main svg node has width and height attributes
        attrs = self.getNodeAttributes(dom_svg)
        level.width  = self.extractFloatFromString(attrs['width'])
        level.height = self.extractFloatFromString(attrs['height'])
        level.rootLayer  = self.recursiveScanningLayers(dom_svg)
        
        dom.unlink()

    def recursiveScanningLayers(self, dom_layer):
        # there can be layers in svg... and each layer can have its own transformation
        rootLayer = Layer(self.getNodeAttributes(dom_layer))
        dom_paths = self.getChildren(dom_layer, 'path')
        for dom_path in dom_paths:
            rootLayer.addPath(self.getNodeAttributes(dom_path))

        dom_layerChildren = self.getChildren(dom_layer, 'g')
        for dom_layerChild in dom_layerChildren:
            rootLayer.addChild(self.recursiveScanningLayers(dom_layerChild))

        return rootLayer

    def getNodeAttributes(self, node):
        """ returns them as a dic.
        key   = attribute name
        value = attribute value
        """
        dic = {}
        
        if node.hasAttributes() == True:
            for i in xrange(node.attributes.length):
                attr = node.attributes.item(i)
                dic[attr.nodeName] = attr.nodeValue
        
        return dic
    
    def getChildren(self, node, childsName):
        """ returns them as a list
        """
        childs = []
        
        for i in xrange(node.childNodes.length):
            child = node.childNodes.item(i)
            if child.nodeName == childsName:
                childs.append(child)
                
        return childs

def initModule():
    Factory().registerObject('transform_parser', TransformParser)
    Factory().registerObject('XML_parser',       XMLParser)
    Factory().registerObject('label_parser',     LabelParser)
    Factory().registerObject('path_parser',      PathParser)

initModule()

