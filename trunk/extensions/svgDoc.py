from lxml.etree import Element
from inkex import addNS, NSS
import log
from svgnode import newImageNode

class SvgDoc():
    def __init__(self):
        self.document = None
        self.patterns = {}

    def setDoc(self, document):
        self.document = document

    def getAndCreateMetadata(self):
        (node, value) = self.getMetaData()
        if node is None:
            self.createMetadata('')
            (node, value) = self.getMetaData()
        return (node, value)

    def getMetaData(self):
        metadata = ''
        descriptionNode = None
        descriptionNodes = self.document.xpath('//dc:description',
                                               namespaces=NSS)
        if descriptionNodes is not None and len(descriptionNodes) > 0:
            descriptionNode = descriptionNodes[0]
            metadata = descriptionNode.text
            if metadata is None:
                metadata = ''

        return (descriptionNode, metadata)

    def createMetadata(self, textValue):
        self.svg  = self.document.getroot()

        # create only dc:description or metadata/RDF/dc:description ?
        metadatas = self.document.xpath('//svg:metadata', namespaces=NSS)
        if metadatas is None or len(metadatas) == 0:
            metadata = Element(addNS('metadata', 'svg'))
            metadata.set('id', 'metadatasvg2lvl')
            self.svg.append(metadata)
        else:
            metadata = metadatas[0]

        rdfs = metadata.xpath('//rdf:RDF', namespaces=NSS)
        if rdfs is None or len(rdfs) == 0:
            rdf = Element(addNS('RDF', 'rdf'))
            metadata.append(rdf)
        else:
            rdf = rdfs[0]

        works = rdf.xpath('//cc:Work', namespaces=NSS)
        if works is None or len(works) == 0:            
            work = Element(addNS('Work', 'cc'))
            work.set(addNS('about', 'rdf'), '')
            rdf.append(work)
        else:
            work = works[0]

        formats = work.xpath('//dc:format', namespaces=NSS)
        if formats is None or len(formats) == 0:
            format = Element(addNS('format', 'dc'))
            format.text = 'image/svg+xml'
            work.append(format)

        types = work.xpath('//dc:type', namespaces=NSS)
        if types is None or len(types) == 0:
            typeNode = Element(addNS('type', 'dc'))
            typeNode.set(addNS('resource', 'rdf'),
                         'http://purl.org/dc/dcmitype/StillImage')
            work.append(typeNode)


        description = Element(addNS('description', 'dc'))
        description.text = textValue
        work.append(description)

    def getPatterns(self):
        patterns = self.document.xpath('//pattern')
        for pattern in patterns:
            patternId = pattern.get('id')
            self.patterns[patternId] = pattern
        self.defs = self.document.xpath('/svg:svg/svg:defs', namespaces=NSS)[0]
        self.svg  = self.document.getroot()

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
                log.outMsg(msg)
                raise Exception(msg)
            textureFilename = textures[textureName]['file']
            pattern = Element(addNS('pattern', 'svg'))
            for name, value in [('patternUnits', 'userSpaceOnUse'),
                                ('width',        str(textureWidth)),
                                ('height',       str(textureHeight)),
                                ('id',           'pattern_%s' % textureName)]:
                pattern.set(name, value)
            image = newImageNode(textureFilename,
                                 (textureWidth, textureHeight),
                                 (0, 0), textureName)
            pattern.append(image)
            self.patterns[patternId] = pattern
            self.defs.append(pattern)
        return patternId
