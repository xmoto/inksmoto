from factory import Factory
from stats   import Stats
from vector  import Vector
from bezier  import Bezier
from parametricArc import ParametricArc
import math
import logging, log

class Element:
    def __init__(self, *args, **keywords):
        self.id                  = keywords['id']
        self.elementInformations = keywords['elementInformations']
        self.vertex              = keywords['vertex']
        self.transformMatrix     = keywords['transformMatrix']
        self.content = []
        self.initBoundingBox()

    def applyRatioAndTransformOnPoint(self, x, y):
        x, y = self.transformMatrix.applyOnPoint(x, y)
        return self.applyRatioOnPoint(x, y)
    
    def applyRatioOnPoint(self, x, y):
        return x * self.ratio, y * self.ratio

    def preProcessVertex(self):
        # apply transformations on block vertex
        self.vertex = Factory().createObject('path_parser').parse(self.vertex)
        for element, valuesDic in self.vertex:
            if element != 'Z':
                x, y = self.applyRatioAndTransformOnPoint(valuesDic['x'], valuesDic['y'])
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
        self.content.append("\t</zone>")
        
        Stats().addZone(self.id)
        
        return self.content
 


class Block(Element):
    def __init__(self, *args, **keywords):
        Element.__init__(self, *args, **keywords)

    def writeBlockHead(self):
        self.content.append("\t<block id=\"%s\">" % self.curBlock)
        self.content.append("\t\t<position x=\"-%f\" y=\"%f\" %s/>"
                            % (self.newWidth/2, self.newHeight/2, self.positionParams))
        self.content.append("\t\t<usetexture id=\"%s\"/>" % self.texture)
        
    def writeContent(self, **keywords):
        """
        - block:
          * background
          * dynamic
          * usetexture=texture_name
        """
        self.curBlockCounter = 0
        self.curBlock    = self.id
        self.ratio       = keywords['ratio']
        self.newWidth    = keywords['newWidth']
        self.newHeight   = keywords['newHeight']
        self.smooth      = keywords['smooth']

        logging.debug("Block::writeContent:: matrix: %s" % (self.transformMatrix))

        self.positionParams = ""
        if self.elementInformations.has_key('background'):
            self.positionParams += " background=\"true\""
        if self.elementInformations.has_key('dynamic'):
            self.positionParams += " dynamic=\"true\""

        self.texture = "default"
        if self.elementInformations.has_key('usetexture'):
            self.texture = self.elementInformations['usetexture']
            
        self.edgeTexture = ""
        if self.elementInformations.has_key('edgeTexture'):
            self.edgeTexture = self.elementInformations['edgeTexture']

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


    def generateBezierCurvePoints(self, point1, controlPoint1, controlPoint2, point2):
        bezierCurve = Bezier((point1, controlPoint1, controlPoint2, point2))
        maxSegmentLength = self.newWidth / 100.0
        return bezierCurve.splitCurve(maxSegmentLength)

    def generateParametricArcPoints(self, (x1, y1), (x2, y2), (rx, ry), x_rot, fA, fS):
            arc = ParametricArc((x1, y1), (x2, y2), (rx, ry), x_rot, fA, fS)
            maxSegmentLength = self.newWidth / 100.0
            return arc.splitArc(maxSegmentLength)
    
    def preProcessVertex(self):
        # apply transformations on block vertex
        self.vertex = Factory().createObject('path_parser').parse(self.vertex)
        
        # as we add new vertex, we need a new list to store them
        tmp = []
        for element, valuesDic in self.vertex:
            if element == 'C':
                x1, y1 = valuesDic['x1'], valuesDic['y1']
                x2, y2 = valuesDic['x2'], valuesDic['y2']
                x,  y  = valuesDic['x'],  valuesDic['y']
                tmp.extend(self.generateBezierCurvePoints((self.lastX, self.lastY), (x1, y1), (x2, y2), (x, y)))
            elif element == 'A':
                x,  y  = valuesDic['x'],  valuesDic['y']
                rx, ry = valuesDic['rx'], valuesDic['ry']
                tmp.extend(self.generateParametricArcPoints((self.lastX, self.lastY), (x, y), (rx,ry),
                                                            valuesDic['x_axis_rotation'], 
                                                            valuesDic['large_arc_flag'], 
                                                            valuesDic['sweep_flag']))
            elif element != 'Z':
                tmp.append([element, valuesDic])

            if valuesDic is not None:
                self.lastX = valuesDic['x']
                self.lastY = valuesDic['y']
        
        # apply transformation on the block        
        for line, lineDic in tmp:
            x, y = self.applyRatioAndTransformOnPoint(lineDic['x'],  lineDic['y'])
            lineDic['x'], lineDic['y']  = x, y

        self.vertex = tmp
                    

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
            
        # xmoto wants clockwise polygons
        self.transformBlockClockwise()
        self.optimizeVertex()
        
        # need at least 3 vertex in a block
        if len(self.currentBlockVertex) < 3:
            raise Exception("A block need at least three vertex (block %s)" % (self.curBlock))

        # if the last vertex is the same as the first, xmoto crashes
        def sameVertex(v1, v2):
            return (abs(v1[0] - v2[0]) < 0.00001) and (abs(v1[1] - v2[1]) < 0.00001)

        if sameVertex(self.currentBlockVertex[0], self.currentBlockVertex[-1]):
            self.currentBlockVertex = self.currentBlockVertex[:-1]
            logging.info("%s: remove last vertex" % self.curBlock)
        
        self.addBlockEdge()

        for (x,y,edge) in self.currentBlockVertex:
            edgeInfo = ""
            if edge and self.edgeTexture != '':
                edgeInfo = " edge=\"%s\"" % self.edgeTexture
                
            self.content.append("\t\t<vertex x=\"%f\" y=\"-%f\" %s/>" % (x,y,edgeInfo))

        return ret

    def addBlockEdge(self):
        tmpVertex = []        
        firstVertice = self.currentBlockVertex[0]

        # add the first vertice so we can test the last one
        self.currentBlockVertex.append(firstVertice)
        
        for i in xrange(len(self.currentBlockVertex)-1):
            x1,y1 = self.currentBlockVertex[i]
            x2,y2 = self.currentBlockVertex[i+1]
            normal = Vector(x2-x1, y2-y1).normal()
            
            if normal.y() > 0:
                tmpVertex.append((x1, y1, True))
            else:
                tmpVertex.append((x1, y1, False))

        self.currentBlockVertex = tmpVertex

    def optimizeVertex(self):
        def calculateAngleBetweenThreePoints(pt1, pt2, pt3):
            x,y = range(2)
            v1 = Vector(pt2[x]-pt1[x], pt2[y]-pt1[y])
            v2 = Vector(pt3[x]-pt2[x], pt3[y]-pt2[y])          
            angle = v1.angle(v2)
            
            return angle

        tmpVertex = []
        nbVertexBefore = len(self.currentBlockVertex)
        
        tmpVertex.append(self.currentBlockVertex[0])
        self.lastx = self.currentBlockVertex[0][0]
        self.lasty = self.currentBlockVertex[0][1]

        def smooth2limit(smooth):
            # smooth [0 : 100] -> [0.1 : 0.001]
            return smooth * -0.00099 + 0.1

        xLimit = smooth2limit(self.smooth) * self.newWidth
        yLimit = smooth2limit(self.smooth) * self.newHeight
        angleLimit = 0.0314
        for i in xrange(1, len(self.currentBlockVertex)-1):
            x2,y2 = self.currentBlockVertex[i]
            x3,y3 = self.currentBlockVertex[i+1]
            angle = calculateAngleBetweenThreePoints((self.lastx,self.lasty), (x2,y2), (x3,y3))
            if ((abs(x2 - self.lastx) > xLimit or abs(y2 - self.lasty) > yLimit) and abs(angle) > angleLimit) or (abs(angle) > angleLimit*10):
                tmpVertex.append((x2, y2))
                self.lastx = x2
                self.lasty = y2
                Stats().addOptimizedVertice(self.curBlock)

        tmpVertex.append(self.currentBlockVertex[-1])
        self.currentBlockVertex = tmpVertex
        nbVertexAfter = len(self.currentBlockVertex)
        
        logging.info("optimizeVertex[%s]:: %d vertex -> %d vertex" % (self.curBlock,
                                                                         nbVertexBefore,
                                                                         nbVertexAfter))

    def addVertice(self, x, y):
        self.currentBlockVertex.append((x, y))
        self.addVerticeToBoundingBox(x, y)
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
    def __init__(self, *args, **keywords):
        Element.__init__(self, *args, **keywords)
        Stats().addEntity(self.id)

    def writeContent(self, **keywords):
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

        self.newWidth  = keywords['newWidth']
        self.newHeight = keywords['newHeight']
        self.ratio     = keywords['ratio']

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
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.5
        self.typeid = 'EndOfLevel'

class Strawberry(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.5
        self.typeid = 'Strawberry'

class PlayerStart(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.4
        self.typeid = 'PlayerStart'

class Sprite(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.4
        self.typeid = 'Sprite'

class Wrecker(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.4
        self.typeid = 'Wrecker'

class ParticleSource(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
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
