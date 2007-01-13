from datetime import date
from stats    import Stats
import elements
import logging, log

class Level:
    def __init__(self):
        self.elements = []
        self.ratio    = 0.05

    def generateLevelDataFromSvg(self, options):
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
        self.smooth    = options.smooth

        self.limits = {}
        self.limits['left']   = -self.lvlWidth/2.0
        self.limits['right']  = self.lvlWidth/2.0
        self.limits['top']    = self.lvlHeight/2.0
        self.limits['bottom'] = -self.lvlHeight/2.0

        self.options = {}
        self.options['id']       = options.id
        self.options['name']     = options.name
        self.options['desc']     = options.desc
        self.options['author']   = options.author
        self.options['date']     = str(date.today())
        self.options['sky']      = options.sky
        self.options['rversion'] = options.rversion
        self.options['lua']      = options.lua


        if self.options['lua'] is not None:
            # TODO
            self.script = ""
        else:
            self.script = ""

        self.createEntitiesAndBlocksFromSvg(self.rootLayer)


    def generateLevelDataFromLvl(self):
        self.createEntitiesAndBlocksFromLvl()



    def generateLvlContent(self):
        Stats().reinitStats()

        # generate level content
        self.content = []
        self.writeLevelHead()
        if self.options['lua'] is not None:
            self.writeLevelScript(self.options['lua'])
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
                                                     smooth      = self.smooth))
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

        layer.elements.extend([path.createElementRepresentedByPath() for path in layer.paths])

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
        self.content.append("<level id=\"%s\">" % self.options['id'])
        self.content.append("\t<info>")
        self.content.append("\t\t<name>%s</name>" % self.options['name'])
        self.content.append("\t\t<description>%s</description>" % self.options['desc'])
        self.content.append("\t\t<author>%s</author>" % self.options['author'])
        self.content.append("\t\t<date>%s</date>" % self.options['date'])
        self.content.append("\t\t<sky>%s</sky>" % self.options['sky'])
        self.content.append("\t</info>")
        self.content.append("\t<limits left=\"%d\" right=\"%d\" top=\"%d\" bottom=\"%d\"/>"
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
