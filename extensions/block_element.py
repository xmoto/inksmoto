from factory  import Factory
from stats    import Stats
from vector   import Vector
from bezier   import Bezier
from elements import Element
from parametricArc  import ParametricArc
from xmotoTools import getValue, createIfAbsent
from math     import fabs
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
        def removeNonNormal(blockPositionParams):
            """ only static blocks in layers other than main """
            for key in ['background', 'dynamic', 'physics']:
                if key in blockPositionParams:
                    del blockPositionParams[key]

        self.curBlockCounter = 0
        self.curBlock  = self.id
        self.ratio     = keywords['ratio']
        self.newWidth  = keywords['newWidth']
        self.newHeight = keywords['newHeight']
        self.smooth    = keywords['smooth']
        level          = keywords['level']

        createIfAbsent(self.infos, 'position')

        if 'x' not in self.infos['position'] or 'y' not in self.infos['position']:
            self.infos['position']['x'] = '%f' % (-self.newWidth/2.0)
            self.infos['position']['y'] = '%f' % (self.newHeight/2.0)

        layerNumber = self.infos['layerid']
        del self.infos['layerid']
        layerLevel = level.layerInfos[layerNumber]
        if layerLevel == 'static':
            pass
        elif layerLevel == '2ndStatic':
            self.infos['position']['islayer'] = "true"
            removeNonNormal(self.infos['position'])
        else:
            self.infos['position']['islayer'] = "true"
            self.infos['position']['layerid'] = str(level.layerBlock2Level[layerNumber])
            removeNonNormal(self.infos['position'])

        if 'usetexture' not in self.infos:
            self.infos['usetexture'] = {'id':'default'}
            
        self.edgeTexture = ""
        self.downEdgeTexture = ""
        if 'edge' in self.infos:
            if 'texture' in self.infos['edge']:
                self.edgeTexture = self.infos['edge']['texture']
            if 'downtexture' in self.infos['edge']:
                self.downEdgeTexture = self.infos['edge']['downtexture']
            del self.infos['edge']

        if 'physics' in self.infos:
            if 'infinitemass' in self.infos['physics']:
                if self.infos['physics']['infinitemass'] == 'true':
                    self.infos['physics']['mass'] = 'INFINITY'
                    del self.infos['physics']['infinitemass']

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
        return Bezier((point1, controlPoint1, controlPoint2, point2)).splitCurve()

    def generateParametricArcPoints(self, (x1, y1), (x2, y2), (rx, ry), x_rot, fA, fS):
        return ParametricArc((x1, y1), (x2, y2), (rx, ry), x_rot, fA, fS).splitArc()
    
    def preProcessVertex(self):
        # apply transformations on block vertex
        self.vertex = Factory().createObject('path_parser').parse(self.vertex)

        # first, check if the path is a circle
        # M x y
        # A rx ry 0 1 1 x1 y
        # A rx ry 0 1 1 x y
        # Z
	if len(self.vertex) == 4:
            if self.vertex[0][0] == 'M' and self.vertex[1][0] == 'A' and self.vertex[2][0] == 'A' and self.vertex[3][0] == 'Z':
                (element, values) = self.vertex[0]
                (x, y) = values['x'], values['y']

                (element, values) = self.vertex[1]
                (rx1, ry1, x1, y1) = values['rx'], values['ry'], values['x'], values['y']

                (element, values) = self.vertex[2]
                (rx2, ry2, x2, y2) = values['rx'], values['ry'], values['x'], values['y']

                if rx1 == rx2 and ry1 == ry2 and x2 == x and y1 == y and y2 == y:
                    (element, values) = self.vertex[1]
                    (xAxRot, laFlag, sFlag) = values['x_axis_rotation'], values['large_arc_flag'], values['sweep_flag']

                    if xAxRot == 0 and laFlag == 1 and sFlag == 1:
                        (element, values) = self.vertex[2]
                        (xAxRot, laFlag, sFlag) = values['x_axis_rotation'], values['large_arc_flag'], values['sweep_flag']

                        if xAxRot == 0 and laFlag == 1 and sFlag == 1:
                            # we have a circle
                            self.infos['collision'] = {}
                            self.infos['collision']['type'] = 'Circle'
                            self.infos['collision']['radius'] = 0.0

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
        self.aabb.reinit()
        for line, lineDic in tmp:
            if lineDic is not None:
                x, y = self.applyRatioAndTransformOnPoint(lineDic['x'],  lineDic['y'])
                lineDic['x'], lineDic['y']  = x, y
                self.aabb.addPoint(x, y)

        self.vertex = tmp

        # the position of the block is the center of its bounding box
        posx = self.aabb.cx()
        posy = self.aabb.cy()
        oldPosx = float(self.infos['position']['x'])
        oldPosy = float(self.infos['position']['y'])
        self.xDiff = posx - oldPosx
        self.yDiff = posy - oldPosy
        self.infos['position']['x'] = '%f' % (posx)
        self.infos['position']['y'] = '%f' % (posy)

        if 'collision' in self.infos:
            self.infos['collision']['radius'] = self.aabb.width() / 2.0

    def initBlockInfos(self):
        self.lastx = 99999
        self.lasty = 99999

    def writeBlockVertex(self):
        # some block got no final 'z'...
        ret = False
        self.currentBlockVertex = []
        self.initBlockInfos()
        self.aabb.reinit()

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
            logging.debug("%s: remove last vertex" % self.curBlock)
        
        # need at least 3 vertex in a block
        if len(self.currentBlockVertex) < 3:
            logging.info("A block need at least three vertex (block %s)" % (self.curBlock))
            return ret

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
        drawmethod = getValue(self.infos, 'edges', 'drawmethod')
        if drawmethod in [None, 'angle']:
            angle = getValue(self.infos, 'edges', 'angle')
            if angle in [None, '270']:
                tmpVertex = []        
                firstVertice = self.currentBlockVertex[0]

                # add the first vertice so we can test the last one
                self.currentBlockVertex.append(firstVertice)

                for i in xrange(len(self.currentBlockVertex)-1):
                    x1,y1 = self.currentBlockVertex[i]
                    x2,y2 = self.currentBlockVertex[i+1]

                    if x1 == x2 and y1 == y2:
                        continue

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

                    if x1 == x2 and y1 == y2:
                        continue

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
        
        logging.debug("optimizeVertex[%s]:: %d vertex -> %d vertex" % (self.curBlock,
                                                                       nbVertexBefore,
                                                                       nbVertexAfter))

    def addVertice(self, x, y):
        # we change the block pos
        x = x - self.xDiff
        y = y + self.yDiff
        self.currentBlockVertex.append((x, y))
        self.aabb.addPoint(x, y)
        Stats().addVertice(self.curBlock)

    def transformBlockClockwise(self):
        """
        http://astronomy.swin.edu.au/~pbourke/geometry/clockwise/
        """
        length = len(self.currentBlockVertex)
        if length < 2:
            return

        # put the block in his own space
        translatedVertex = [(x-self.aabb.x(), y-self.aabb.y()) for x, y in self.currentBlockVertex]

        area = 0
        for i in range(len(translatedVertex)-1):
            (x1, y1) = translatedVertex[i]
            (x2, y2) = translatedVertex[i+1]
            area += x1 * (-y2) - x2 * (-y1)

        if area > 0:
            logging.debug("reverse the block %s. block area: %f"
                          % (self.curBlock, area))
            self.currentBlockVertex.reverse()
        else:
            logging.debug("block not reverse %s. block area: %f"
                          % (self.curBlock, area))

        # use the area to put the block mass for chipmunk
        self.mass = fabs(area)

def initModule():
    Factory().registerObject('Block_element', Block)

initModule()
