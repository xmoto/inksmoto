from lxml.etree import Element
from inkex import addNS, NSS
import log, logging
from svgnode import newImageNode, getImageId, newUseNode

class SvgDoc():
    def __init__(self):
        self.document = None
        self.patterns = {}
        self.images = {}

    def setDoc(self, document):
        self.document = document

    def getAndCreateMetadataNode(self):
        node = self.getMetaDataNode()
        if node is None:
            self.createMetadata('')
            node = self.getMetaDataNode()
        return node

    def getMetaDataNode(self):
        node = None
        nodes = self.document.xpath('//dc:description',
                                    namespaces=NSS)
        if nodes is not None and len(nodes) > 0:
            node = nodes[0]

        return node

    def getMetaDataValue(self):
        return self.getMetaData()[1]

    def getMetaData(self):
        metadata = ''
        node = self.getMetaDataNode()

        if node is not None:
            metadata = node.text
            if metadata is None:
                metadata = ''

        return (node, metadata)

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
        if len(self.patterns) > 0:
            return

        patterns = self.document.xpath('//pattern')
        for pattern in patterns:
            patternId = pattern.get('id')
            self.patterns[patternId] = pattern
        self.defs = self.document.xpath('/svg:svg/svg:defs', namespaces=NSS)[0]
        self.svg  = self.document.getroot()

    def getImages(self):
        if len(self.images) > 0:
            return

        self.getPatterns()

        images = self.document.xpath('/svg:svg/svg:defs/svg:image',
                                     namespaces=NSS)
        for image in images:
            imageId = image.get('id')
            self.images[imageId] = image

    def addPattern(self, textureName, textures, scale):
        self.getPatterns()

        width  = 92.0
        height = 92.0

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
                                ('width', str(width)),
                                ('height', str(height)),
                                ('id', patternId)]:
                pattern.set(name, value)

            imageId = self.addImage(textureName, textures, width, height)
            use = newUseNode('use_%s' % patternId, 0, 0, imageId)
            pattern.append(use)
            self.patterns[patternId] = pattern
            self.defs.append(pattern)

        if scale != 1.0:
            def inkscape2xmoto(scale):
                if scale == 0.0:
                    return 0.0
                else:
                    return 1.0 / scale

            scaledPatternId = 'pattern_%s_%.2f' % (textureName, scale)
            scale = inkscape2xmoto(scale)

            if scaledPatternId not in self.patterns.keys():
                pattern = Element(addNS('pattern', 'svg'))
                for name, value in [('id',
                                     scaledPatternId),
                                    ('patternTransform',
                                     'scale(%f, %f)' % (scale, scale)),
                                    (addNS('href', 'xlink'),
                                     '#' + patternId)]:
                    pattern.set(name, value)

                self.patterns[scaledPatternId] = pattern
                self.defs.append(pattern)

                patternId = scaledPatternId

        return patternId

    def addImage(self, imageName, bitmaps, width=92.0, height=92.0):
        self.getImages()

        imageId = getImageId(imageName, width, height)
        if imageId not in self.images.keys():
            if imageName not in bitmaps.keys():
                msg = 'The image %s is not an existing one.' % imageName
                log.outMsg(msg)
                raise Exception(msg)

            imageFilename = bitmaps[imageName]['file']
            image = newImageNode(imageFilename, (width, height),
                                 (0, 0), imageName)
            self.images[imageId] = image
            self.defs.append(image)
        return imageId
