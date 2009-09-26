#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import log, logging
from factory  import Factory
from vector   import Vector
from bezier   import Bezier
from elements import Element
from parametricArc  import ParametricArc
from xmotoTools import getValue, createIfAbsent, delWithoutExcept, getIfPresent
from xmotoTools import getBoolValue
from math import fabs

def smooth2limit(smooth):
    # smooth [0 : 100] -> [0.1 : 0.001] * 100
    return (smooth * -0.00099 + 0.1) * 100

class Block(Element):
    def writeBlockHead(self):
        def writeMaterial(side, texture, material):
            content = "\t\t\t<material name=\"%s\" edge=\"%s\" color_r=\"%d\" \
color_g=\"%d\" color_b=\"%d\" color_a=\"%d\"" % (side, texture, material[0][0],
                                                 material[0][1], material[0][2],
                                                 material[0][3])
            if material[1] != -1.0:
                content += " scale=\"%f\"" % material[1]
            if material[2] != -1.0:
                content += " depth=\"%f\"" % material[2]
            content += " />"
            self.content.append(content)
        
        self.content.append("\t<block id=\"%s\">" % self.curBlock)
        if self.u_material is not None or self.d_material is not None:
            delWithoutExcept(self.infos, 'edges')
            if self.edgeAngle != 270.0:
                self.content.append("\t\t<edges angle=\"%f\">" % self.edgeAngle)
            else:
                self.content.append("\t\t<edges>")
            if self.u_material is not None:
                writeMaterial('u', self.edgeTexture, self.u_material)
            if self.d_material is not None:
                writeMaterial('d', self.downEdgeTexture, self.d_material)
            self.content.append("\t\t</edges>")
        self.addElementParams()

    def writeContent(self, options, level):
        """
        - block:
          * background
          * dynamic
          * usetexture=texture_name
        """

        def removeNonNormal(posParams, keys):
            """ only static blocks in layers other than main """
            for key in keys:
                if key in posParams:
                    del posParams[key]
                    
        def removeNonMain(posParams):
            removeNonNormal(posParams, ['background', 'physics'])

        def removeForLayer(posParams):
            removeNonNormal(posParams, ['background', 'dynamic', 'physics'])


        def getEdgeColorAndScale(prefix):
            r = int(getValue(self.infos, 'edge', '%s_r' % prefix, default=255))
            g = int(getValue(self.infos, 'edge', '%s_g' % prefix, default=255))
            b = int(getValue(self.infos, 'edge', '%s_b' % prefix, default=255))
            a = int(getValue(self.infos, 'edge', '%s_a' % prefix, default=255))
            scale = float(getValue(self.infos, 'edge',
                                   '%s_scale' % prefix, default=-1.0))
            depth = float(getValue(self.infos, 'edge',
                                   '%s_depth' % prefix, default=-1.0))
            return ((r, g, b, a), scale, depth)

        self.curBlockCounter = 0
        self.curBlock  = self._id
        self.ratio = options['ratio']
        self.newWidth  = options['width']
        self.newHeight = options['height']
        self.smooth = options['smooth']
        useSmooth = getBoolValue(self.infos, 'position', '_usesmooth')
        if useSmooth == True:
            (present, smooth) = getIfPresent(self.infos, 'position', '_smooth')
            if present == True:
                self.smooth = 90.0+float(smooth)

        createIfAbsent(self.infos, 'position')

        if ('x' not in self.infos['position']
            or 'y' not in self.infos['position']):
            self.infos['position']['x'] = '%f' % (-self.newWidth/2.0)
            self.infos['position']['y'] = '%f' % (self.newHeight/2.0)

        layerNumber = self.infos['layerid']
        del self.infos['layerid']
        layerLevel = level.getLayersType()[layerNumber]
        if layerLevel == 'static':
            pass
        elif layerLevel == '2ndStatic':
            self.infos['position']['islayer'] = "true"
            removeNonMain(self.infos['position'])
        else:
            self.infos['position']['islayer'] = "true"
            lid = str(level.getLayerBlock2Level()[layerNumber])
            self.infos['position']['layerid'] = lid
            removeForLayer(self.infos['position'])

        if 'usetexture' not in self.infos:
            self.infos['usetexture'] = {'id':'default'}
            
        self.edgeTexture = getValue(self.infos, 'edge', 'texture', '')
        self.downEdgeTexture = getValue(self.infos, 'edge', 'downtexture', '')
        for prefix in ['u', 'd']:
            ((r, g, b, a), scale, depth) = getEdgeColorAndScale(prefix)
            if r != 255 or g != 255 or b != 255 or scale != -1.0 or depth != -1.0:
                self.__dict__['%s_material' % prefix] = ((r, g, b, a), scale, depth)
            else:
                self.__dict__['%s_material' % prefix] = None
        self.edgeAngle = float(getValue(self.infos, 'edges', 'angle', 270.0))
        delWithoutExcept(self.infos, 'edge')

        if 'physics' in self.infos:
            if 'infinitemass' in self.infos['physics']:
                if self.infos['physics']['infinitemass'] == 'true':
                    self.infos['physics']['mass'] = 'INFINITY'
                    del self.infos['physics']['infinitemass']

        self.preProcessVertex()

        for vertex in self.blocks:
            self.writeBlockHead()
            self.writeBlockVertex(vertex)
            self.content.append("\t</block>")

            self.curBlockCounter += 1
            self.curBlock = self._id + str(self.curBlockCounter)
            
        return self.content

    def isCircle(self, vertex):
        """
         M x y
         A rx ry 0 1 1 x1 y
         A rx ry 0 1 1 x y
        """
        if len(vertex) == 3:
            if (vertex[0][0] == 'M' and vertex[1][0] == 'A'
                and vertex[2][0] == 'A'):

                # to acces values with simplepath format
                (Arx, Ary, Aaxis, Aarc, Asweep, Ax, Ay) = range(-7, 0)
                (Mx, My) = range(-2, 0)

                values = vertex[0][1]
                (x, y) = values[Mx], values[My]

                values = vertex[1][1]
                (rx1, ry1) = values[Arx], values[Ary]
                y1 = values[Ay]

                values = vertex[2][1]
                (rx2, ry2) = values[Arx], values[Ary]
                (x2, y2) = values[Ax], values[Ay]

                if (rx1 == rx2 and ry1 == ry2
                    and x2 == x and y1 == y and y2 == y):
                    values = vertex[1][1]
                    (xAxRot, laFlag, sFlag) = (values[Aaxis], values[Aarc],
                                               values[Asweep])

                    if xAxRot == 0 and laFlag == 1 and sFlag == 1:
                        values = vertex[2][1]
                        (xAxRot, laFlag, sFlag) = (values[Aaxis], values[Aarc],
                                                   values[Asweep])

                        if xAxRot == 0 and laFlag == 1 and sFlag == 1:
                            # we have a circle
                            self.infos['collision'] = {}
                            self.infos['collision']['type'] = 'Circle'
                            # the radius will be compute later
                            self.infos['collision']['radius'] = 0.0
        

    def convertInLines(self):
        """
        convert C and A to lines.
        """
        # if smooth = 100, limit = 1.0, is smooth is smaller, limit is
        # bigger and less points are generated by splitCurve
        limit = smooth2limit(self.smooth) * 10

        # to acces values with simplepath format
        (Cx1, Cy1, Cx2, Cy2, Cx, Cy) = range(-6, 0)
        (Arx, Ary, Aaxis, Aarc, Asweep, Ax, Ay) = range(-7, 0)
        (x, y) = range(-2, 0)

        newBlocks = []
        for vertex in self.blocks:
            # as we add new vertex, we need a new list to store them
            tmp = []
            (lastX, lastY) = (0, 0)
            for element, values in vertex:
                if element == 'C':
                    tmp.extend(Bezier(((lastX, lastY),
                                       (values[Cx1], values[Cy1]),
                                       (values[Cx2], values[Cy2]),
                                       (values[Cx],  values[Cy])
                                       )
                                      ).splitCurve(limit))
                elif element == 'A':
                    tmp.extend(ParametricArc((lastX, lastY),
                                             (values[Ax],  values[Ay]),
                                             (values[Arx], values[Ary]),
                                             values[Aaxis], values[Aarc],
                                             values[Asweep]).splitArc())
                else:
                    tmp.append((values[x], values[y]))

                lastX = values[x]
                lastY = values[y]

            newBlocks.append(tmp)
        self.blocks = newBlocks

    def preProcessVertex(self):
        """ apply transformations on block vertex """
        self.blocks = Factory().create('path_parser').parse(self.pathsInfos)

        if len(self.blocks) == 1:
            self.isCircle(self.blocks[0])

        self.convertInLines()
        self.transform()
        self.aabb.reinit()
        self.addToAABB()

        # the position of the block is the center of its bounding box
        posx = self.aabb.cx()
        posy = self.aabb.cy()
        oldPosx = float(self.infos['position']['x'])
        oldPosy = float(self.infos['position']['y'])
        self.xDiff = posx - oldPosx
        self.yDiff = posy - oldPosy
        self.infos['position']['x'] = str(posx)
        self.infos['position']['y'] = str(posy)

        # update the vertex (x, y)
        newBlocks = []
        for vertex in self.blocks:
            vertex = [(x - self.xDiff, y + self.yDiff) for x, y in vertex]
            newBlocks.append(vertex)
        self.blocks = newBlocks

        if 'collision' in self.infos:
            self.infos['collision']['radius'] = self.aabb.width() / 2.0

    def writeBlockVertex(self, vertex):
        # some block got no final 'z'...
        self.aabb.reinit()
        [self.aabb.addPoint(x, y) for x, y in vertex]

        # xmoto wants clockwise polygons
        vertex = self.transformBlockClockwise(vertex)
        vertex = self.optimizeVertex(vertex)
        
        # if the last vertex is the same as the first, xmoto crashes
        def sameVertex(v1, v2):
            return ((abs(v1[0] - v2[0]) < 0.00001)
                    and (abs(v1[1] - v2[1]) < 0.00001))

        if sameVertex(vertex[0], vertex[-1]):
            vertex = vertex[:-1]
            logging.debug("%s: remove last vertex" % self.curBlock)
        
        # need at least 3 vertex in a block
        if len(vertex) < 3:
            logging.info("A block need at least three vertex (block %s)"
                         % (self.curBlock))
            return

        vertex = self.addBlockEdge(vertex)

        # if a material is defined, we have to use it instead of the
        # texture
        if self.u_material is None:
            upEdge = self.edgeTexture
        else:
            upEdge = 'u'
        if self.d_material is None:
            downEdge = self.downEdgeTexture
        else:
            downEdge = 'd'

        wEdge = "\t\t<vertex x=\"%f\" y=\"%f\" edge=\"%s\"/>"
        woEdge = "\t\t<vertex x=\"%f\" y=\"%f\"/>"
        for (x, y, upSide) in vertex:
            if upSide == True:
                if self.edgeTexture != '':
                    self.content.append(wEdge % (x, -y, upEdge))
                else:
                    self.content.append(woEdge % (x, -y))
            else:
                if self.downEdgeTexture != '':
                    self.content.append(wEdge % (x, -y, downEdge))
                else:
                    self.content.append(woEdge % (x, -y))

    def addBlockEdge(self, vertex):
        tmpVertex = []        
        firstVertice = vertex[0]
        vertex.append(firstVertice)

        for i in xrange(len(vertex)-1):
            x1, y1 = vertex[i]
            x2, y2 = vertex[i+1]

            if x1 == x2 and y1 == y2:
                continue

            r = Vector(x2-x1, y2-y1).normal().rotate(self.edgeAngle - 270.0)

            if r.y > 0:
                tmpVertex.append((x1, y1, True))
            else:
                tmpVertex.append((x1, y1, False))

        return tmpVertex

    def optimizeVertex(self, vertex):
        def angleBetweenThreePoints(pt1, pt2, pt3):
            v1 = Vector(pt2[0]-pt1[0], pt2[1]-pt1[1])
            v2 = Vector(pt3[0]-pt2[0], pt3[1]-pt2[1])
            angle = v1.angle(v2)
            return angle

        tmpVertex = []
        tmpVertex.append(vertex[0])
        lastX = vertex[0][0]
        lastY = vertex[0][1]

        limit = smooth2limit(self.smooth)
        angleLimit = 0.0314
        for i in xrange(1, len(vertex)-1):
            x2, y2 = vertex[i]
            x3, y3 = vertex[i+1]
            angle = angleBetweenThreePoints((lastX, lastY),
                                            (x2, y2),
                                            (x3, y3))
            if (((abs(x2 - lastX) > limit or abs(y2 - lastY) > limit)
                 and abs(angle) > angleLimit)
                or (abs(angle) > angleLimit*10)):
                tmpVertex.append((x2, y2))
                lastX = x2
                lastY = y2

        tmpVertex.append(vertex[-1])
        return tmpVertex

    def transformBlockClockwise(self, vertex):
        """
        http://astronomy.swin.edu.au/~pbourke/geometry/clockwise/
        """
        length = len(vertex)
        if length < 2:
            return

        # put the block in his own space
        translatedVertex = [(x-self.aabb.x(), y-self.aabb.y())
                            for x, y in vertex]

        area = 0
        for i in range(len(translatedVertex)-1):
            (x1, y1) = translatedVertex[i]
            (x2, y2) = translatedVertex[i+1]
            area += x1 * (-y2) - x2 * (-y1)

        if area > 0:
            vertex.reverse()

        # use the area to put the block mass for chipmunk
        self.mass = fabs(area)

        return vertex

def initModule():
    Factory().register('Block_element', Block)

initModule()
