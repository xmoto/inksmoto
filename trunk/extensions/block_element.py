from factory  import Factory
from stats    import Stats
from vector   import Vector
from bezier   import Bezier
from elements import Element
from parametricArc  import ParametricArc
from xmotoTools import getValue
import logging, log

class Block(Element):
    def __init__(self, *args, **keywords):
        Element.__init__(self, *args, **keywords)

    def writeBlockHead(self):
        self.content.append("\t<block id=\"%s\">" % self.curBlock)
        self.addElementParams()

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
        level            = keywords['level']

        logging.debug("Block::writeContent:: matrix: %s" % (self.transformMatrix))

        if 'position' not in self.elementInformations:
            self.elementInformations['position'] = {}

        if 'x' not in self.elementInformations['position'] or 'y' not in self.elementInformations['position']:
            self.elementInformations['position']['x'] = '%f' % (-self.newWidth/2.0)
            self.elementInformations['position']['y'] = '%f' % (self.newHeight/2.0)

        layerNumber = self.elementInformations['layerid']
        del self.elementInformations['layerid']
        layerLevel = level.layerInfos[layerNumber]
        if layerLevel == 'static':
            pass
        elif layerLevel == '2ndStatic':
            self.elementInformations['position']['islayer'] = "true"
        else:
            self.elementInformations['position']['islayer'] = "true"
            self.elementInformations['position']['layerid'] = str(level.layerBlock2Level[layerNumber])
            # blocks in layer have to be 'normal' blocks (no background and/or dynamic blocks)
            for key in ['background', 'dynamic']:
                if key in self.elementInformations['position']:
                    del self.elementInformations['position'][key]

        if 'usetexture' not in self.elementInformations:
            self.elementInformations['usetexture'] = {'id':'default'}
            
        self.edgeTexture = ""
        self.downEdgeTexture = ""
        if 'edge' in self.elementInformations:
            if 'texture' in self.elementInformations['edge']:
                self.edgeTexture = self.elementInformations['edge']['texture']
            if 'downtexture' in self.elementInformations['edge']:
                self.downEdgeTexture = self.elementInformations['edge']['downtexture']
            del self.elementInformations['edge']

        Stats().addBlock(self.curBlock)

        self.preProcessVertex()

        self.writeBlockHead()
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
        # now that ratio is fixed, we use a fixed maxSegmentLength
        #maxSegmentLength = self.newWidth / 100.0
        maxSegmentLength = 1.0
        return bezierCurve.splitCurve(maxSegmentLength)

    def generateParametricArcPoints(self, (x1, y1), (x2, y2), (rx, ry), x_rot, fA, fS):
        arc = ParametricArc((x1, y1), (x2, y2), (rx, ry), x_rot, fA, fS)
        #maxSegmentLength = self.newWidth / 100.0
        maxSegmentLength = 1.0
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
            else:
                tmp.append([element, valuesDic])

            if valuesDic is not None:
                self.lastX = valuesDic['x']
                self.lastY = valuesDic['y']
        
        # apply transformation on the block
        self.initBoundingBox()
        for line, lineDic in tmp:
            if lineDic is not None:
                x, y = self.applyRatioAndTransformOnPoint(lineDic['x'],  lineDic['y'])
                lineDic['x'], lineDic['y']  = x, y
                self.addVerticeToBoundingBox(x, y)

        self.vertex = tmp

        # the position of the block is the center of its bounding box
        posx = (self.minX + self.maxX) / 2.0
        posy = (self.minY + self.maxY) / 2.0
        oldPosx = float(self.elementInformations['position']['x'])
        oldPosy = float(self.elementInformations['position']['y'])
        self.xDiff = posx - oldPosx
        self.yDiff = posy - oldPosy
        self.elementInformations['position']['x'] = '%f' % (posx)
        self.elementInformations['position']['y'] = '%f' % (posy)

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
        
        # if the last vertex is the same as the first, xmoto crashes
        def sameVertex(v1, v2):
            return (abs(v1[0] - v2[0]) < 0.00001) and (abs(v1[1] - v2[1]) < 0.00001)

        if sameVertex(self.currentBlockVertex[0], self.currentBlockVertex[-1]):
            self.currentBlockVertex = self.currentBlockVertex[:-1]
            logging.info("%s: remove last vertex" % self.curBlock)
        
        # need at least 3 vertex in a block
        if len(self.currentBlockVertex) < 3:
            raise Exception("A block need at least three vertex (block %s)" % (self.curBlock))

        self.addBlockEdge()

        for (x,y,edge) in self.currentBlockVertex:
            if edge:
                if self.edgeTexture != '':
                    self.content.append("\t\t<vertex x=\"%f\" y=\"%f\" edge=\"%s\"/>" % (x,-y,self.edgeTexture))
                else:
                    self.content.append("\t\t<vertex x=\"%f\" y=\"%f\"/>" % (x,-y))
            else:
                if self.downEdgeTexture != '':
                    self.content.append("\t\t<vertex x=\"%f\" y=\"%f\" edge=\"%s\"/>" % (x,-y,self.downEdgeTexture))
                else:
                    self.content.append("\t\t<vertex x=\"%f\" y=\"%f\"/>" % (x,-y))

        return ret

    def addBlockEdge(self):
        drawmethod = getValue(self.elementInformations, 'edges', 'drawmethod')
        if drawmethod in [None, 'angle']:
            angle = getValue(self.elementInformations, 'edges', 'angle')
            if angle in [None, 270.0]:
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
            else:
                tmpVertex = []        
                firstVertice = self.currentBlockVertex[0]
                self.currentBlockVertex.append(firstVertice)

                for i in xrange(len(self.currentBlockVertex)-1):
                    x1,y1 = self.currentBlockVertex[i]
                    x2,y2 = self.currentBlockVertex[i+1]

                    rotate = Vector(x2-x1, y2-y1).rotate(float(angle))

                    if rotate.y() > 0:
                        tmpVertex.append((x1, y1, True))
                    else:
                        tmpVertex.append((x1, y1, False))

                self.currentBlockVertex = tmpVertex
        elif drawmethod in ['in', 'out']:
            self.currentBlockVertex = [(x, y, True) for (x, y) in self.currentBlockVertex]

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
            # smooth [0 : 100] -> [0.1 : 0.001] * 100
            return (smooth * -0.00099 + 0.1) * 100

        #xLimit = smooth2limit(self.smooth) * self.newWidth
        #yLimit = smooth2limit(self.smooth) * self.newHeight
        xLimit = smooth2limit(self.smooth)
        yLimit = smooth2limit(self.smooth)
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
        # we change the block pos
        x = x - self.xDiff
        y = y + self.yDiff
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

def initModule():
    Factory().registerObject('Block_element', Block)

initModule()
