from singleton       import Singleton
import xml.dom.minidom
from layer           import Layer
from factory         import Factory
from unit            import UnitsConvertor
from inkex           import NSS
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
        type5=val5|namespace1:type1=val1|namespace2:type2=val2|namespace2:type3|namespace3:type4=val4
        and the output is a dic:
        {type5:val5, namespace1:{'type1':val1}, namespace2:{'type2':val2, 'type3':''}, namespace3:{'type4':'val4'}}        
        """
        dic = {}
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
    return elementSep.join([keyValueSep.join([str(value) for value in param if value != None]) for param in dic.items()])

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
        delim = re.compile(r'[ \t\r\n,]+')
        command = re.compile(r'[MLHVCSQTAZmlhvcsqtaz]')
        parameter = re.compile(r'(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)')
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
            m = parameter.match(d, offset)
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
                    raise Exception("Unknown element in svg path: %s" % curElement)
            except StopIteration:
                break

        return self.parsedElements

class XMLParser:
    __metaclass__ = Singleton

    def __init__(self):
        pass
    
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

    def getChildText(self, node, childName):
        return self.getNodeText(node.getElementsByTagName(childName)[0])        

    def getNodeText(self, node):
        return self.getText(node.childNodes)

    def getText(self, nodeList):
        text = ""
        for node in nodeList:
            if node.nodeType == node.TEXT_NODE:
                text += node.data
        return text


class XMLParserLvl(XMLParser):
    def __init__(self):
        pass

    def parse(self, lvlFile, level):
        dom = xml.dom.minidom.parse(lvlFile)

        dom_level    = dom.getElementsByTagName('level')[0]
        dom_limits   = dom_level.getElementsByTagName('limits')[0]
        dom_blocks   = dom_level.getElementsByTagName('block')
        dom_entities = dom_level.getElementsByTagName('entity')
        dom_zones    = dom_level.getElementsByTagName('zone')
        dom_script   = dom_level.getElementsByTagName('script')[0]

        level.options  = self.getInfos(dom_level)
        level.limits   = self.getNodeAttributes(dom_limits)
        level.blocks   = self.getBlocks(dom_blocks)
        level.entities = self.getEntities(dom_entities)
        level.zones    = self.getZones(dom_zones)
        level.script   = self.getNodeText(dom_script)

        dom.unlink()

    def getInfos(self, dom_level):
        options = {}
        attrs = self.getNodeAttributes(dom_level)
        options['id'] = attrs['id']

        if attrs.has_key('rversion'):
            options['rversion'] = attrs['rversion']

        dom_info = dom_level.getElementsByTagName('info')[0]

        options['name']   = self.getChildText(dom_info, 'name')
        options['description'] = self.getChildText(dom_info, 'description')
        options['author'] = self.getChildText(dom_info, 'author')
        options['date']   = self.getChildText(dom_info, 'date')
        options['sky']    = self.getChildText(dom_info, 'sky')

        return options

    def getNodeInfos(self, dom_nodes):
        nodeInfos = {}

        # go through node children, create one dictionnary for each different child type
        for dom_node in dom_nodes:
            # text nodes are empty lines in the xml file
            if dom_node.nodeType is not dom_node.TEXT_NODE:
                # if first time we meet a child type, create its dictionnary
                if dom_node.tagName not in nodeInfos:
                    nodeInfos[dom_node.tagName] = {}
                # if the dict has been transformed into a list, append the attrs dict to its end
                if type(nodeInfos[dom_node.tagName]) == list:
                    nodeInfos[dom_node.tagName].append(self.getNodeAttributes(dom_node))
                # add the attrs to the existing dict.
                # if there's a key in the attrs dict which is already into the existing dict, then
                # create a list whose elements are the differents dict
                else:
                    found = False
                    attrs = self.getNodeAttributes(dom_node)
                    for key in nodeInfos[dom_node.tagName].keys():
                        if key in attrs:
                            nodeInfos[dom_node.tagName] = [nodeInfos[dom_node.tagName], attrs]
                            found = True
                            break

                    if not found:
                        nodeInfos[dom_node.tagName].update(self.getNodeAttributes(dom_node))
        return nodeInfos

    def getBlocks(self, dom_blocks):
        blocks = {}

        for dom_block in dom_blocks:
            attrs      = self.getNodeAttributes(dom_block)
            id         = attrs['id']
            blocks[id] = self.getNodeInfos(dom_block.childNodes)
        return blocks

    def getEntities(self, dom_entities):
        entities = {}
        # go through every entities
        for dom_entity in dom_entities:
            # get entity's id and typeid from its attributes
            attrs = self.getNodeAttributes(dom_entity)
            id = attrs['id']
            typeId = attrs['typeid']

            if not entities.has_key(typeId):
                entities[typeId] = {}
            entities[typeId][id] = self.getNodeInfos(dom_entity.childNodes)
        return entities            

    def getZones(self, dom_zones):
        zones = {}
        for dom_zone in dom_zones:
            attrs = self.getNodeAttributes(dom_zone)
            id = attrs['id']
            zones[id] = self.getNodeInfos(dom_zone.childNodes)
        return zones


class XMLParserSvg(XMLParser):
    def __init__(self):
        pass

    def parse(self, svgFile, level):
        dom = xml.dom.minidom.parse(svgFile)

        # there is a main svg node in a svg file
        dom_svg = dom.getElementsByTagName("svg")[0]

        # the main svg node has width and height attributes
        attrs = self.getNodeAttributes(dom_svg)
        level.svgWidth  = UnitsConvertor(attrs['width']).convert('px')
        level.svgHeight = UnitsConvertor(attrs['height']).convert('px')

        levelOptions = dom.getElementsByTagNameNS(NSS['dc'], 'description')
        if len(levelOptions) == 0:
            raise Exception("Level options are not set.")
        description = self.getNodeText(levelOptions[0])
        labelParser = Factory().createObject('label_parser')
        level.options = labelParser.parse(description)

        level.rootLayer = self.recursiveScanningLayers(dom_svg)
        
        dom.unlink()

    def recursiveScanningLayers(self, dom_layer):
        # there can be layers in svg... and each layer can have its own transformation
        rootLayer = Layer(self.getNodeAttributes(dom_layer))
        dom_paths = self.getChildren(dom_layer, 'path')
        for dom_path in dom_paths:
            rootLayer.addPath(self.getNodeAttributes(dom_path))

        dom_rects = self.getChildren(dom_layer, 'rect')
        for dom_rect in dom_rects:
            rootLayer.addRect(self.getNodeAttributes(dom_rect))

        dom_layerChildren = self.getChildren(dom_layer, 'g')
        for dom_layerChild in dom_layerChildren:
            rootLayer.addChild(self.recursiveScanningLayers(dom_layerChild))

        return rootLayer


def initModule():
    Factory().registerObject('transform_parser', TransformParser)
    Factory().registerObject('XML_parserSvg',    XMLParserSvg)
    Factory().registerObject('XML_parserLvl',    XMLParserLvl)
    Factory().registerObject('label_parser',     LabelParser)
    Factory().registerObject('path_parser',      PathParser)
    Factory().registerObject('style_parser',     StyleParser)

initModule()

