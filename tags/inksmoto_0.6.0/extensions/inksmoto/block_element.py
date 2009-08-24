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
from xmotoTools import getValue, createIfAbsent, delWithoutExcept
from math import fabs

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
        def removeNonNormal(blockPositionParams):
            """ only static blocks in layers other than main """
            for key in ['background', 'dynamic', 'physics']:
                if key in blockPositionParams:
                    del blockPositionParams[key]

        def getEdgeColorAndScale(prefix):
            r = int(getValue(self.infos, 'edge', '%s_r' % prefix, default=255))
            g = int(getValue(self.infos, 'edge', '%s_g' % prefix, default=255))
            b = int(getValue(self.infos, 'edge', '%s_b' % prefix, default=255))
            a = int(getValue(self.infos, 'edge', '%s_a' % prefix, default=255))
            scale = float(getValue(self.infos, 'edge', '%s_scale' % prefix, default=-1.0))
            depth = float(getValue(self.infos, 'edge', '%s_depth' % prefix, default=-1.0))
            return ((r, g, b, a), scale, depth)

        self.curBlockCounter = 0
        self.curBlock  = self._id
        self.ratio = options['ratio']
        self.newWidth  = options['width']
        self.newHeight = options['height']
        self.smooth = options['smooth']

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
            removeNonNormal(self.infos['position'])
        else:
            self.infos['position']['islayer'] = "true"
            lid = str(level.getLayerBlock2Level()[layerNumber])
            self.infos['position']['layerid'] = lid
            removeNonNormal(self.infos['position'])

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

        self.writeBlockHead()
        # a block can have multi path in it...
        while self.writeBlockVertex() == True:
            self.content.append("\t</block>")

            self.curBlockCounter += 1
            self.curBlock = self._id + str(self.curBlockCounter)
            
            self.writeBlockHead()
            
        self.content.append("\t</block>")

        return self.content

    def isCircle(self):
        """ M x y
         A rx ry 0 1 1 x1 y
         A rx ry 0 1 1 x y
         Z """
        if len(self.vertex) == 4:
            if (self.vertex[0][0] == 'M' and self.vertex[1][0] == 'A'
                and self.vertex[2][0] == 'A' and self.vertex[3][0] == 'Z'):
                values = self.vertex[0][1]
                (x, y) = values['x'], values['y']

                values = self.vertex[1][1]
                (rx1, ry1) = values['rx'], values['ry']
                y1 = values['y']

                values = self.vertex[2][1]
                (rx2, ry2) = values['rx'], values['ry']
                (x2, y2) = values['x'], values['y']

                if (rx1 == rx2 and ry1 == ry2
                    and x2 == x and y1 == y and y2 == y):
                    values = self.vertex[1][1]
                    (xAxRot, laFlag, sFlag) = (values['x_axis_rotation'],
                                               values['large_arc_flag'],
                                               values['sweep_flag'])

                    if xAxRot == 0 and laFlag == 1 and sFlag == 1:
                        values = self.vertex[2][1]
                        (xAxRot, laFlag, sFlag) = (values['x_axis_rotation'],
                                                   values['large_arc_flag'],
                                                   values['sweep_flag'])

                        if xAxRot == 0 and laFlag == 1 and sFlag == 1:
                            # we have a circle
                            self.infos['collision'] = {}
                            self.infos['collision']['type'] = 'Circle'
                            # the radius will be compute later
                            self.infos['collision']['radius'] = 0.0
        


    def preProcessVertex(self):
        """ apply transformations on block vertex """
        self.vertex = Factory().createObject('path_parser').parse(self.vertex)

        self.isCircle()

        # as we add new vertex, we need a new list to store them
        tmp = []
        (lastX, lastY) = (0, 0)
        for element, valuesDic in self.vertex:
            if element == 'C':
                tmp.extend(Bezier(((lastX, lastY),
                                   (valuesDic['x1'], valuesDic['y1']),
                                   (valuesDic['x2'], valuesDic['y2']),
                                   (valuesDic['x'],  valuesDic['y'])
                                   )
                                  ).splitCurve())
            elif element == 'A':
                tmp.extend(ParametricArc((lastX, lastY),
                                         (valuesDic['x'],  valuesDic['y']),
                                         (valuesDic['rx'], valuesDic['ry']),
                                         valuesDic['x_axis_rotation'], 
                                         valuesDic['large_arc_flag'], 
                                         valuesDic['sweep_flag']).splitArc())
            else:
                tmp.append([element, valuesDic])

            if valuesDic is not None:
                lastX = valuesDic['x']
                lastY = valuesDic['y']
        
        # apply transformation on the block
        self.aabb.reinit()
        for (line, lineDic) in tmp:
            if lineDic is not None:
                (x, y) = (lineDic['x'], lineDic['y'])
                (x, y) = self.applyRatioAndTransformOnPoint(x, y)
                (lineDic['x'], lineDic['y']) = (x, y)
                self.aabb.addPoint(x, y)

        self.vertex = tmp

        # the position of the block is the center of its bounding box
        posx = self.aabb.cx()
        posy = self.aabb.cy()
        oldPosx = float(self.infos['position']['x'])
        oldPosy = float(self.infos['position']['y'])
        self.xDiff = posx - oldPosx
        self.yDiff = posy - oldPosy
        self.infos['position']['x'] = str(posx)
        self.infos['position']['y'] = str(posy)

        if 'collision' in self.infos:
            self.infos['collision']['radius'] = self.aabb.width() / 2.0

    def writeBlockVertex(self):
        # some block got no final 'z'...
        ret = False
        self.curBlockVertex = []
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
            return ((abs(v1[0] - v2[0]) < 0.00001)
                    and (abs(v1[1] - v2[1]) < 0.00001))

        if sameVertex(self.curBlockVertex[0], self.curBlockVertex[-1]):
            self.curBlockVertex = self.curBlockVertex[:-1]
            logging.debug("%s: remove last vertex" % self.curBlock)
        
        # need at least 3 vertex in a block
        if len(self.curBlockVertex) < 3:
            logging.info("A block need at least three vertex (block %s)"
                         % (self.curBlock))
            return ret

        self.addBlockEdge()

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
        for (x, y, upSide) in self.curBlockVertex:
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

        return ret

    def addBlockEdge(self):
        tmpVertex = []        
        firstVertice = self.curBlockVertex[0]
        self.curBlockVertex.append(firstVertice)

        for i in xrange(len(self.curBlockVertex)-1):
            x1, y1 = self.curBlockVertex[i]
            x2, y2 = self.curBlockVertex[i+1]

            if x1 == x2 and y1 == y2:
                continue

            r = Vector(x2-x1, y2-y1).normal().rotate(self.edgeAngle - 270.0)

            if r.y() > 0:
                tmpVertex.append((x1, y1, True))
            else:
                tmpVertex.append((x1, y1, False))

        self.curBlockVertex = tmpVertex

    def optimizeVertex(self):
        def angleBetweenThreePoints(pt1, pt2, pt3):
            v1 = Vector(pt2[0]-pt1[0], pt2[1]-pt1[1])
            v2 = Vector(pt3[0]-pt2[0], pt3[1]-pt2[1])          
            angle = v1.angle(v2)
            return angle

        def smooth2limit(smooth):
            # smooth [0 : 100] -> [0.1 : 0.001] * 100
            return (smooth * -0.00099 + 0.1) * 100

        tmpVertex = []
        tmpVertex.append(self.curBlockVertex[0])
        lastX = self.curBlockVertex[0][0]
        lastY = self.curBlockVertex[0][1]

        limit = smooth2limit(self.smooth)
        angleLimit = 0.0314
        for i in xrange(1, len(self.curBlockVertex)-1):
            x2, y2 = self.curBlockVertex[i]
            x3, y3 = self.curBlockVertex[i+1]
            angle = angleBetweenThreePoints((lastX, lastY),
                                            (x2, y2),
                                            (x3, y3))
            if (((abs(x2 - lastX) > limit or abs(y2 - lastY) > limit)
                 and abs(angle) > angleLimit)
                or (abs(angle) > angleLimit*10)):
                tmpVertex.append((x2, y2))
                lastX = x2
                lastY = y2

        tmpVertex.append(self.curBlockVertex[-1])
        self.curBlockVertex = tmpVertex

    def addVertice(self, x, y):
        # we change the block pos
        x = x - self.xDiff
        y = y + self.yDiff
        self.curBlockVertex.append((x, y))
        self.aabb.addPoint(x, y)

    def transformBlockClockwise(self):
        """
        http://astronomy.swin.edu.au/~pbourke/geometry/clockwise/
        """
        length = len(self.curBlockVertex)
        if length < 2:
            return

        # put the block in his own space
        translatedVertex = [(x-self.aabb.x(), y-self.aabb.y())
                            for x, y in self.curBlockVertex]

        area = 0
        for i in range(len(translatedVertex)-1):
            (x1, y1) = translatedVertex[i]
            (x2, y2) = translatedVertex[i+1]
            area += x1 * (-y2) - x2 * (-y1)

        if area > 0:
            self.curBlockVertex.reverse()

        # use the area to put the block mass for chipmunk
        self.mass = fabs(area)

def initModule():
    Factory().registerObject('Block_element', Block)

initModule()
