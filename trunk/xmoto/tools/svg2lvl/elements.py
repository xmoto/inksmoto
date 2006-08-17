from factory import Factory
from stats   import Stats
import logging, log

class Element:
    def __init__(self, *args):
        self.id                  = args[0]
        self.elementInformations = args[1]
        self.vertex              = args[2]
        self.transformMatrix     = args[3]
        self.content = []
        self.initBoundingBox()

    def preProcessVertex(self):
        def applyRatioAndTransformOnPoint(x, y):
            x, y = self.transformMatrix.applyOnPoint(x, y)
            return x * self.ratio, y * self.ratio

        # apply transformations on block vertex
        self.vertex = Factory().createObject('path_parser').parse(self.vertex)
        for element, valuesDic in self.vertex:
            if element != 'Z':
                x, y = applyRatioAndTransformOnPoint(valuesDic['x'], valuesDic['y'])
                valuesDic['x'] = x
                valuesDic['y'] = y
                self.addVerticeToBoundingBox(x, y)

    def pointInLevelSpace(self, x, y):
        x =  x - self.newWidth/2
        y = -y + self.newHeight/2
        return x, y
        

    def addVerticeToBoundingBox(self, x, y):
        if x > self.maxX:
            self.maxX = x
        if x < self.minX:
            self.minX = x
        if y > self.maxY:
            self.maxY = y
        if y < self.minY:
            self.minY = y

    def initBoundingBox(self):
        self.minX = 99999
        self.maxX = -99999
        self.minY = 99999
        self.maxY = -99999
                

class Zone(Element):
    def __init__(self, *args):
        Element.__init__(self, *args)

    def writeContent(self, newWidth, newHeight, ratio):
        """
        <zone id="FirstZone">
                <box left="-29.000000" right="-17.000000" top="6.000000" bottom="0.000000"/>
        </zone>
        """
        logging.debug("Zone::writeContent:: matrix: %s" % (self.transformMatrix))

        self.newWidth  = newWidth
        self.newHeight = newHeight
        self.ratio     = ratio

        self.preProcessVertex()
        maxX, minY = self.pointInLevelSpace(self.maxX, self.maxY)
        minX, maxY = self.pointInLevelSpace(self.minX, self.minY)

        self.content.append("\t<zone id=\"%s\">" % (self.id))
        self.content.append("\t\t<box left=\"%f\" right=\"%f\" top=\"%f\" bottom=\"%f\"/>" 
                            % (minX, maxX, maxY, minY))
        self.content.append("\t</zone>")
        
        Stats().addZone(self.id)
        
        return self.content
 


class Block(Element):
    def __init__(self, *args):
        Element.__init__(self, *args)

    def writeBlockHead(self):
        self.content.append("\t<block id=\"%s\">" % self.curBlock)
        self.content.append("\t\t<position x=\"-%f\" y=\"%f\" %s/>"
                            % (self.newWidth/2, self.newHeight/2, self.positionParams))
        self.content.append("\t\t<usetexture id=\"%s\"/>" % self.texture)
        
    def writeContent(self, newWidth, newHeight, ratio):
        """
        - block:
          * background
          * dynamic
          * usetexture=texture_name
        """
        self.curBlockCounter = 0
        self.curBlock  = self.id
        self.ratio     = ratio
        self.newWidth  = newWidth
        self.newHeight = newHeight

        logging.debug("Block::writeContent:: matrix: %s" % (self.transformMatrix))

        self.positionParams = ""
        if self.elementInformations.has_key('background'):
            self.positionParams += " background=\"true\""
        if self.elementInformations.has_key('dynamic'):
            self.positionParams += " dynamic=\"true\""

        self.texture = "default"
        if self.elementInformations.has_key('usetexture'):
            self.texture = self.elementInformations['usetexture']

        Stats().addBlock(self.curBlock)

        self.writeBlockHead()

        if self.curBlock == 'PlayerStart0':
            logging.debug("Block::WriteContent::posx=%f posy=%f" % (-newWidth/2, newHeight/2))

        self.preProcessVertex()
        # a block can have multi path in it...
        while self.writeBlockVertex() == True:
            self.content.append("\t</block>")

            self.curBlockCounter += 1
            self.curBlock = self.id + str(self.curBlockCounter)
            
            self.writeBlockHead()
            Stats().addBlock("%s" % (self.curBlock))
            

        self.content.append("\t</block>")

        return self.content

    def initBlockInfos(self):
        self.lastx = 99999
        self.lasty = 99999

    def writeBlockVertex(self):
        # some block got no final 'z'...
        ret = False
        self.currentBlockVertex = []
        self.initBlockInfos()
        self.initBoundingBox()

        while len(self.vertex) != 0:
            element, valuesDic = self.vertex.pop(0)
            
            if element == 'Z':
                ret = (len(self.vertex) > 0)
                break
           
            x, y = valuesDic['x'], valuesDic['y']
            self.addVertice(x, y)

        # if the last vertex is the same as the first, xmoto crashes
        self.currentBlockVertex = self.currentBlockVertex[:-1]
        
        # need at least 3 vertex in a block
        if len(self.currentBlockVertex) < 3:
            raise Exception("A block need at least three vertex (block %s)" % (self.curBlock))

        # xmoto wants clockwise polygons
        self.transformBlockClockwise()
        for (x,y) in self.currentBlockVertex:
            self.content.append("\t\t<vertex x=\"%f\" y=\"-%f\"/>" % (x,y))

        return ret

    def addVertice(self, x, y):
        # if two following vertice are almost the same, keep only the first.
        # 'null ...' exception otherwise when you open the level in xmoto...
        if abs(x - self.lastx) > 0.05 or (y - self.lasty) > 0.05:
            self.currentBlockVertex.append((x, y))
            self.addVerticeToBoundingBox(x, y)
            self.lastx = x
            self.lasty = y

            Stats().addVertice(self.curBlock)

    def transformBlockClockwise(self):
        """
        http://astronomy.swin.edu.au/~pbourke/geometry/clockwise/
        """
        length = len(self.currentBlockVertex)
        if length < 2:
            return

        # put the block in his own space
        translatedVertex = [(x-self.minX, y-self.minY) for x, y in self.currentBlockVertex]

        area = 0
        for i in range(len(translatedVertex)-1):
            (x1, y1) = translatedVertex[i]
            (x2, y2) = translatedVertex[i+1]
            area += x1 * (-y2) - x2 * (-y1)

        if area > 0:
            logging.info("reverse the block %s. block area: %f"
                         % (self.curBlock, area))
            self.currentBlockVertex.reverse()
        else:
            logging.info("block not reverse %s. block area: %f"
                         % (self.curBlock, area))
            

class Entity(Element):
    def __init__(self, *args):
        Element.__init__(self, *args)
        Stats().addEntity(self.id)

    def writeContent(self, newWidth, newHeight, ratio):
        """
        - entity:
          * typeid=[PlayerStart|EndOfLevel|Strawberry|Wrecker|ParticleSource|Sprite]
          * size=float_number (the entity colision radius)
          * param_name=param_value
          ** available params are (there's more of them):
             z     (for Sprite)
             name  (for Sprite)
             style (for every entity)
             type  (for ParticleSource)
        """
        logging.debug("Entity-%s-::writeContent:: matrix: %s" % (self.typeid, self.transformMatrix))

        self.newWidth  = newWidth
        self.newHeight = newHeight
        self.ratio     = ratio

        self.preProcessVertex()
        self.content.append("\t<entity id=\"%s\" typeid=\"%s\">" % (self.id, self.typeid))
        if self.elementInformations.has_key('size'):
            radius = self.elementInformations['size']
        else:
            radius = self.radius

        self.content.append("\t\t<size r=\"%s\"/>" % str(radius))
        self.content.append("\t\t<position x=\"%f\" y=\"%f\"/>" % self.getEntityPos())
        self.writeEntityParams()
        self.content.append("\t</entity>")
        
        return self.content

    def getEntityPos(self):
        # a path alway begin with 'M posx posy'
        element, valuesDic = self.vertex.pop(0)
        return self.pointInLevelSpace(valuesDic['x'], valuesDic['y'])

    def writeEntityParams(self):
        #<param name="xxx" value="yyy"        
        del self.elementInformations['typeid']
        
        self.content.extend(["\t\t<param name=\"%s\" value=\"%s\"/>" % (key, str(value)) for key, value in self.elementInformations.iteritems()])
        
        if not self.elementInformations.has_key('style'):
            self.content.append("\t\t<param name=\"style\" value=\"default\"/>")


class EndOfLevel(Entity):
    def __init__(self, *args):
        Entity.__init__(self, *args)
        self.radius = 0.5
        self.typeid = 'EndOfLevel'

class Strawberry(Entity):
    def __init__(self, *args):
        Entity.__init__(self, *args)
        self.radius = 0.5
        self.typeid = 'Strawberry'

class PlayerStart(Entity):
    def __init__(self, *args):
        Entity.__init__(self, *args)
        self.radius = 0.4
        self.typeid = 'PlayerStart'

class Sprite(Entity):
    def __init__(self, *args):
        Entity.__init__(self, *args)
        self.radius = 0.4
        self.typeid = 'Sprite'

class Wrecker(Entity):
    def __init__(self, *args):
        Entity.__init__(self, *args)
        self.radius = 0.4
        self.typeid = 'Wrecker'

class ParticleSource(Entity):
    def __init__(self, *args):
        Entity.__init__(self, *args)
        self.radius = 0.4
        self.typeid = 'ParticleSource'

def initModule():
    Factory().registerObject('Block_element',          Block)
    Factory().registerObject('EndOfLevel_element',     EndOfLevel)
    Factory().registerObject('Strawberry_element',     Strawberry)
    Factory().registerObject('PlayerStart_element',    PlayerStart)
    Factory().registerObject('Sprite_element',         Sprite)
    Factory().registerObject('Wrecker_element',        Wrecker)
    Factory().registerObject('ParticleSource_element', ParticleSource)
    Factory().registerObject('Zone_element',           Zone)

initModule()
