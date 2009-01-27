from factory  import Factory
from elements import Element
import logging

class Zone(Element):
    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)

    def writeContent(self, **kwargs):
        """
        <zone id="FirstZone">
                <box left="-29.0" right="-17.0" top="6.0" bottom="0.0"/>
        </zone>
        """
        logging.debug("Zone::writeContent:: matrix: %s" % (self.matrix))

        self.newWidth  = kwargs['newWidth']
        self.newHeight = kwargs['newHeight']
        self.ratio     = kwargs['ratio']

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
