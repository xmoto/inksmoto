from lxml.etree import Element
from inkex import addNS, NSS
import log, logging
from svgnode import newImageNode, getImageId, newUseNode
from xmotoTools import getValue

class SvgDoc():
    def __init__(self, document=None):
        self.document = document
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

    def updateLayerInfos(self, layersInfos):
        """ when an user updates the svg ordering in inkscape, he has
        to open the layers properties window in order to the layers
        infos in the metadatas to be updated.  put this updates into
        this function so that it can be called from the .lvl creation
        code and from the layerinfos window
        """
        def extractIndexFromKey(key):
            return int(key[len('layer_'):-len('_id')])

        # metadata layerId -> layerIndex
        oldLayersIdToIndex = {}
        maxLayerIndex = -1
        for (key, layerId) in layersInfos.iteritems():
            if key[-3:] != '_id':
                continue
            layerIndex = extractIndexFromKey(key)
            if layerIndex > maxLayerIndex:
                maxLayerIndex = layerIndex
            oldLayersIdToIndex[layerId] = layerIndex

        # svg layers
        layers = self.document.xpath('/svg:svg/svg:g', namespaces=NSS)
        nblayers = len(layers)

        # svg layerId -> layerLabel
        layersLabel = []
        for layer in layers:
            layerId = layer.get('id')
            layerLabel = layer.get(addNS('label', 'inkscape'), '')
            layersLabel.append((layerId, layerLabel))

        # existing layers in the right order
        layersIdToIndexToSave = []
        for layerIndex in reversed(xrange(nblayers)):
            # get old layer index or create a new one if it's a new layer
            layerLabel = layersLabel[layerIndex][1]
            if layerLabel == "":
                layerLabel = '#' + layerId

            layerId = layersLabel[layerIndex][0]
            if layerId in oldLayersIdToIndex:
                oldLayerIndex = oldLayersIdToIndex[layerId]
            else:
                maxLayerIndex += 1
                oldLayerIndex = maxLayerIndex
                oldLayersIdToIndex[layerId] = oldLayerIndex

            # keep only layers who are still there. reorder them in
            # the metadata in the same order as in the svg
            layersIdToIndexToSave.append((layerId, layerLabel,
                                          layerIndex, oldLayerIndex))

        # keep only the still existing layers
        layers = {}
        numberMainLayers = 0
        for (layerId,
             layerLabel,
             layerIndex,
             oldLayerIndex) in layersIdToIndexToSave:
            prefix = 'layer_%d_' % layerIndex
            prefixOld = 'layer_%d_' % oldLayerIndex
            layers[prefix+'id'] = layerId

            value = getValue(layersInfos, prefixOld+'isused', default='true')
            layers[prefix+'isused'] = value

            value = getValue(layersInfos, prefixOld+'ismain', default='false')
            layers[prefix+'ismain'] = value

            value = getValue(layersInfos, prefixOld+'x', default=1.0)
            layers[prefix+'x'] = value

            value = getValue(layersInfos, prefixOld+'y', default=1.0)
            layers[prefix+'y'] = value

        return (layers, layersIdToIndexToSave)