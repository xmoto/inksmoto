from datetime import date
from stats    import Stats
import elements
import logging, log

class Level:
    def __init__(self):
        self.elements = []

    def generateLvlContent(self, options):
        # the xmoto width of the level is the width of svg in pixel divided by 10.0
        self.newWidth  = self.width * 0.1
        self.ratio     = 0.1
        self.newHeight = float(self.height) * self.ratio

        self.smooth = options.smooth

        Stats().reinitStats()

        self.createEntitiesAndBlocks(self.rootLayer)

        # generate level content
        self.content = []
        self.writeLevelHead(options)
        if options.lua is not None:
            self.writeLevelScript(options.lua)
        self.content.append("\t<limits left=\"-%d\" right=\"%d\" top=\"%d\" bottom=\"-%d\"/>"
                            % (self.newWidth/2, self.newWidth/2, self.newHeight/2, self.newHeight/2))
        self.writeLevelContent(self.rootLayer)
        self.content.append("</level>")

        # print the lvl on stdout so inkscape gets it
        for line in self.content:
            print line

    def generateSvgFile(self, svgFileName, newWidth, scriptName):
        pass

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
            self.content.extend(element.writeContent(newWidth    = self.newWidth,
                                                     newHeight   = self.newHeight,
                                                     ratio       = self.ratio,
                                                     smooth      = self.smooth))


    def createEntitiesAndBlocks(self, layer):
        layer.elements = []

        layer.elements.extend([path.createElementRepresentedByPath() for path in layer.paths])

        for child in layer.children:
            self.createEntitiesAndBlocks(child)

    def writeLevelHead(self, options):
        self.content.append("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        self.content.append("<level id=\"%s\">" % options.id)
        self.content.append("\t<info>")
        self.content.append("\t\t<name>%s</name>" % options.name)
        self.content.append("\t\t<description>%s</description>" % options.desc)
        self.content.append("\t\t<author>%s</author>" % options.author)
        self.content.append("\t\t<date>%s</date>" % str(date.today()))
        self.content.append("\t\t<sky>%s</sky>" % options.sky)
        self.content.append("\t</info>")
