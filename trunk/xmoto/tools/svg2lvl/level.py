from stats import Stats
import elements
import logging, log

class Level:
    def __init__(self):
        self.elements = []

    def generateLvlFile(self, levelFileName, newWidth, scriptName):
        levelName = levelFileName[:levelFileName.rfind('.')]
        
        self.newWidth  = float(newWidth)
        self.ratio     = self.newWidth / float(self.width)
        self.newHeight = float(self.height) * self.ratio

        Stats().reinitStats()

        self.createEntitiesAndBlocks(self.rootLayer)

        # generate level content
        self.content = []
        self.writeLevelHead(levelName)
        if scriptName is not None:
            self.writeLevelScript(scriptName)
        self.content.append("\t<limits left=\"-%d\" right=\"%d\" top=\"%d\" bottom=\"-%d\"/>"
                            % (self.newWidth/2, self.newWidth/2, self.newHeight/2, self.newHeight/2))
        self.writeLevelContent(self.rootLayer)
        self.content.append("</level>")

        # add \n to every line
        self.content = [line+'\n' for line in self.content]

        # write lines to the level file
        f = open(levelFileName, 'w')
        f.writelines(self.content)
        f.close

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
            self.content.extend(element.writeContent(self.newWidth,
                                                     self.newHeight,
                                                     self.ratio))


    def createEntitiesAndBlocks(self, layer):
        layer.elements = []

        layer.elements.extend([path.createElementRepresentedByPath() for path in layer.paths])

        for child in layer.children:
            self.createEntitiesAndBlocks(child)

    def writeLevelHead(self, levelName):
        self.content.append("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
        self.content.append("<level id=\"%s\">" % levelName)
        self.content.append("\t<info>")
        self.content.append("\t\t<name>%s</name>" % levelName)
        self.content.append("\t\t<description></description>")
        self.content.append("\t\t<author></author>")
        self.content.append("\t\t<date></date>")
        self.content.append("\t\t<sky>sky1</sky>")
        self.content.append("\t</info>")
