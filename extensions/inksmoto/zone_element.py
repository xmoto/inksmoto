from factory  import Factory
from elements import Element

class Zone(Element):
    def writeContent(self, options, level):
        """
        <zone id="FirstZone">
                <box left="-29.0" right="-17.0" top="6.0" bottom="0.0"/>
        </zone>
        """
        self.newWidth  = options['width']
        self.newHeight = options['height']
        self.ratio     = options['ratio']

        self.preProcessVertex()
        maxX, minY = self.pointInLevelSpace(self.aabb.xmax, self.aabb.ymax)
        minX, maxY = self.pointInLevelSpace(self.aabb.xmin, self.aabb.ymin)

        self.content.append("\t<zone id=\"%s\">" % (self._id))
        line = "\t\t<box left=\"%f\" right=\"%f\" top=\"%f\" bottom=\"%f\"/>"
        self.content.append(line % (minX, maxX, maxY, minY))

        self.addElementParams()
        self.content.append("\t</zone>")

        return self.content

def initModule():
    Factory().registerObject('Zone_element', Zone)

initModule()
