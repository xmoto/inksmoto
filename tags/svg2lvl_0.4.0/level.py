from datetime import date
from stats    import Stats
import elements
import logging, log

class Level:
    def __init__(self):
        self.elements = []
        self.ratio    = 0.05

    def generateLevelDataFromSvg(self):
        """ This function and generateLevelDataFromLvl are responsible
        for putting the data into the elements. Into elements, the
        data have to be the same. If they are created from svg or from
        lvl, they share the same internal representation. Then, from
        this internal representation, you can create either the lvl or
        the svg.
        """
        # the xmoto width of the level is the width of svg in pixel
        # divided by 20.0
        self.lvlWidth  = self.svgWidth  * self.ratio
        self.lvlHeight = self.svgHeight * self.ratio

        self.limits = {}
        self.limits['left']   = -self.lvlWidth/2.0
        self.limits['right']  = self.lvlWidth/2.0
        self.limits['top']    = self.lvlHeight/2.0
        self.limits['bottom'] = -self.lvlHeight/2.0

        # check that require options are set
        if not self.options.has_key('level'):
            raise Exception("Level options not set.")
        if self.options['level']['id'] == '' or self.options['level']['name'] == '':
            raise Exception("Level id or name not set.")

        self.smooth = float(self.options['level']['smooth'])
        # now, smooth is from 1 to 10 in the tkinter window,
        # but it is still from 1 to 100 in svg2lvl
        self.smooth += 90

        # add today date
        self.options['level']['date'] = str(date.today())

        #       if self.options['lua'] is not None:
        #           # TODO
        #           self.script = ""
        #       else:
        #           self.script = ""

        #self.createEntitiesAndBlocksFromSvg(self.rootLayer)
        self.numberLayer = 0
        self.rootLayer.elements = []
        for child in self.rootLayer.children:
            self.createEntitiesAndBlocksFromSvg(child)
            self.numberLayer += 1
        self.createLayerInfos()

    def createLayerInfos(self):
        backLayers = []
        frontLayers = []
        staticLayers = []

        useLayers = True
        if not self.options.has_key('layer'):
            if self.numberLayer > 2:
                msg  = "The svg has more than two layers (the two for the static blocks), "
                msg += "but no layer informations has been put into the svg."
                raise Exception(msg)
            else:
                useLayers = False

        if useLayers == True:
            for layer in xrange(10):
                if self.options['layer']['layer_%d_isused' % layer] == 'false':
                    continue
                if self.options['layer']['layer_%d_isfront' % layer] == 'true':
                    frontLayers.append(layer)
                else:
                    backLayers.append(layer)

        numberStaticLayers = self.numberLayer - (len(frontLayers) + len(backLayers))

        if numberStaticLayers not in [1,2]:
            msg =  "Error ! There's %d layers in the svg. " % self.numberLayer
            msg += "%d back layers, %d front layers. " % (backLayers, frontLayers)
            msg += "So, even if there's 2 static layers, "
            msg += "there's still %d layers with no properties." % (numberStaticLayers-2)
            raise Exception(msg)

        self.layerInfos = []
        self.layerBlock2Level = []

        xmin = 0
        xmax = len(backLayers)
        for layer in xrange(xmin, xmax):
            self.layerInfos.append(backLayers[layer])
            self.layerBlock2Level.append(layer)

        self.layerInfos.append('static')
        self.layerBlock2Level.append(-1)
        if numberStaticLayers == 2:
            self.layerInfos.append('2ndStatic')
            self.layerBlock2Level.append(-1)

        xmin  = xmax
        xmax += len(frontLayers)
        for layer in xrange(xmin, xmax):
            self.layerInfos.append(frontLayers[layer-xmin])
            self.layerBlock2Level.append(layer)

    def generateLevelDataFromLvl(self):
        self.createEntitiesAndBlocksFromLvl()

    def generateLvlContent(self):
        Stats().reinitStats()

        # generate level content
        self.content = []
        self.writeLevelHead()
        if self.options['level']['lua'] not in [None, '']:
            self.writeLevelScript(self.options['level']['lua'])
        self.writeLevelContent(self.rootLayer)
        self.content.append("</level>")

        self.printContentToStdout()


    def generateSvgContent(self):
        self.newWidth  = (float(self.limits['right']) - float(self.limits['left'])) / self.ratio
        self.newHeight = (float(self.limits['top']) - float(self.limits['bottom'])) / self.ratio

        self.createEntitiesAndBlocksFromLvl()

        self.content = []
        self.writeSvgHead()
        self.writeSvgContent()
        self.writeSvgFoot()
        self.printContentToStdout()




    def printContentToStdout(self):
        # print the lvl on stdout so inkscape gets it
        for line in self.content:
            print line

    def writeLevelScript(self, scriptName):
        f = open(scriptName)
        lines = f.readlines()
        f.close
        
        self.content.append("\t<script>")
        self.content.extend([line.replace('<', '&lt;').replace('>', '&gt;').rstrip('\n') for line in lines])
        self.content.append("\t</script>")


    def writeLevelContent(self, layer):
        for child in layer.children:
            self.writeLevelContent(child)

        for element in layer.elements:
            self.content.extend(element.writeContent(newWidth    = self.lvlWidth,
                                                     newHeight   = self.lvlHeight,
                                                     ratio       = self.ratio,
                                                     smooth      = self.smooth,
                                                     level       = self))
#    def createPathFromVertexList(self, vertex, position):
#        path = ""
#
#        posX = float(position['x'])
#        posY = float(position['y'])
#
#        firstPoint = vertex[0]
#        vertex = vertex[1:]
#
#        # add first point
#        path += "M %f,%f " % ((float(firstPoint['x'])+posX)/self.ratio+self.newWidth/2.0, (-float(firstPoint['y'])-posY)/self.ratio+self.newHeight/2.0)
#
#        for vertice in vertex:
#            path += "L %f,%f " % ((float(vertice['x'])+posX)/self.ratio+self.newWidth/2.0, (-float(vertice['y'])-posY)/self.ratio+self.newHeight/2.0)
#
#        path += "L %f,%f " % ((float(firstPoint['x'])+posX)/self.ratio+self.newWidth/2.0, (-float(firstPoint['y'])-posY)/self.ratio+self.newHeight/2.0)
#        path += "z "
#
#        return path
#
#    def writeSvgBlock(self, id, block):
#        self.content.append("    <path")
#        self.content.append("      inkscape:label=\"%s\"" % "")
#        self.content.append("      style=\"%s\"" % "fill:none;fill-opacity:1.0;fill-rule:evenodd;stroke:black;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1")
#        self.content.append("      d=\"%s\"" % self.createPathFromVertexList(block['vertex'], block['position']))
#        self.content.append("      id=\"%s\" />" % id)



    def createEntitiesAndBlocksFromSvg(self, layer):
        layer.elements = []

        layer.elements.extend([path.createElementRepresentedByPath(self.numberLayer) for path in layer.paths])

        for child in layer.children:
            self.createEntitiesAndBlocksFromSvg(child)

    def createEntitiesAndBlocksFromLvl(self):
        self.elements = []
        # blocks
        for id, blockInfos in self.blocks.iteritems():
            block = Factory().createObject('Block_element',
                                           id=id,
                                           input='lvl',
                                           elementInformations=blockInfos)
            self.elements.append(block)

        # entities
        for typeid, ids in self.entities.iteritems():
            elementType = '%s_element' % typeid
            for id, entityInfos in ids.iteritems():
                entity = Factory().createObject(elementType,
                                                id=id,
                                                input='lvl',
                                                elementInformations=entityInfos)
                self.elements.append(entity)

        # zones
        for id, zoneInfos in self.zones.iteritems():
            zone = Factory().createObject('Zone_element',
                                          id=id,
                                          input='lvl',
                                          elementInformations=zoneInfos)
            self.elements.append(zone)
    

    def writeLevelHead(self):
        self.content.append("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        self.content.append("<level id=\"%s\" rversion=\"%s\">" % (self.options['level']['id'], self.options['level']['version']))
        self.content.append("\t<info>")
        self.content.append("\t\t<name>%s</name>" % self.options['level']['name'])
        self.content.append("\t\t<description>%s</description>" % self.options['level']['desc'])
        self.content.append("\t\t<author>%s</author>" % self.options['level']['author'])
        self.content.append("\t\t<date>%s</date>" % self.options['level']['date'])
        if self.options.has_key('sky'):
            sky = "\t\t<sky"
            for skyParam, value in self.options['sky'].iteritems():
                if skyParam != 'tex' and value != '':
                    sky += ' %s="%s"' % (skyParam, value)
            sky += ">%s</sky>" % self.options['sky']['tex']
            self.content.append(sky)
        else:
            self.content.append("\t\t<sky>%s</sky>" % 'sky1')
        if self.options['level']['tex'] != '':
            self.content.append("\t\t<border texture=\"%s\"/>" % self.options['level']['tex'])

        if self.options['level'].has_key('music') and self.options['level']['music'] is not 'None':
            self.content.append("\t\t<music name=\"%s\" />" % self.options['level']['music'])
        self.content.append("\t</info>")

        if self.options.has_key('remplacement'):
            self.content.append("\t<theme_replacements>")
            for key, value in self.options['remplacement'].iteritems():
                if value not in ['None', '', None]:
                    self.content.append("\t\t<sprite_replacement old_name=\"%s\" new_name=\"%s\"/>" % (key, value))
            self.content.append("\t</theme_replacements>")

        if self.options.has_key('layer'):
            self.content.append("\t<layeroffsets>")
            for layerid in self.layerInfos:
                if layerid in ['static', '2ndStatic']:
                    continue
                self.content.append("\t\t<layeroffset x=\"%s\" y=\"%s\" frontlayer=\"%s\"/>" % (self.options['layer']['layer_%d_x' % layerid],
                                                                                                self.options['layer']['layer_%d_y' % layerid],
                                                                                                self.options['layer']['layer_%d_isfront' % layerid]))
            self.content.append("\t</layeroffsets>")


        self.content.append("\t<limits left=\"%f\" right=\"%f\" top=\"%f\" bottom=\"%f\"/>"
                            % (self.limits['left'], self.limits['right'],
                               self.limits['top'], self.limits['bottom']))

    def writeSvgHead(self):
        self.content.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>")
        self.content.append("<!-- Created with Inkscape (http://www.inkscape.org/) -->")
        self.content.append("<svg")
        self.content.append("   xmlns:dc=\"http://purl.org/dc/elements/1.1/\"")
        self.content.append("   xmlns:cc=\"http://web.resource.org/cc/\"")
        self.content.append("   xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"")
        self.content.append("   xmlns:svg=\"http://www.w3.org/2000/svg\"")
        self.content.append("   xmlns=\"http://www.w3.org/2000/svg\"")
        self.content.append("   xmlns:sodipodi=\"http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd\"")
        self.content.append("   xmlns:inkscape=\"http://www.inkscape.org/namespaces/inkscape\"")
        self.content.append("   width=\"%s\""  % self.svgWidth)
        self.content.append("   height=\"%s\"" % self.svgHeight)
        self.content.append("   id=\"svg2\">")
        self.content.append("  <defs")
        self.content.append("     id=\"defs4\" />")
        self.content.append("  <metadata")
        self.content.append("     id=\"metadata7\">")
        self.content.append("    <rdf:RDF>")
        self.content.append("      <cc:Work")
        self.content.append("         rdf:about=\"\">")
        self.content.append("        <dc:format>image/svg+xml</dc:format>")
        self.content.append("        <dc:type")
        self.content.append("           rdf:resource=\"http://purl.org/dc/dcmitype/StillImage\" />")
        self.content.append("      </cc:Work>")
        self.content.append("    </rdf:RDF>")
        self.content.append("  </metadata>")
        self.content.append("  <g id=\"layer1\">")

    def writeSvgFoot(self):
        self.content.append("  </g>")
        self.content.append("</svg>")