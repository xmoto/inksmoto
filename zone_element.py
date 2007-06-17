from factory  import Factory
from stats    import Stats
from elements import Element
import logging, log

class Zone(Element):
    def __init__(self, *args, **keywords):
        Element.__init__(self, *args, **keywords)

    def writeContent(self, **keywords):
        """
        <zone id="FirstZone">
                <box left="-29.000000" right="-17.000000" top="6.000000" bottom="0.000000"/>
        </zone>
        """
        logging.debug("Zone::writeContent:: matrix: %s" % (self.transformMatrix))

        self.newWidth  = keywords['newWidth']
        self.newHeight = keywords['newHeight']
        self.ratio     = keywords['ratio']

        self.preProcessVertex()
        maxX, minY = self.pointInLevelSpace(self.maxX, self.maxY)
        minX, maxY = self.pointInLevelSpace(self.minX, self.minY)

        self.content.append("\t<zone id=\"%s\">" % (self.id))
        self.content.append("\t\t<box left=\"%f\" right=\"%f\" top=\"%f\" bottom=\"%f\"/>" 
                            % (minX, maxX, maxY, minY))
        self.addElementParams()
        self.content.append("\t</zone>")
        
        Stats().addZone(self.id)
        
        return self.content

def initModule():
    Factory().registerObject('Zone_element', Zone)

initModule()
