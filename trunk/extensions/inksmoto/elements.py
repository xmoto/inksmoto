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
from factory import Factory
from aabb import AABB
from xmotoTools import getValue
from matrix import isIdentity

class Element:
    def __init__(self, **kwargs):
        self._id = kwargs['_id']
        self.infos = kwargs['infos']
        self.pathsInfos = kwargs['vertex']
        self.matrix = getValue(kwargs, 'matrix')
        if isIdentity(self.matrix):
            self.matrix = None
        self.content = []
        self.aabb = AABB()

        # added by writeContent
        self.ratio = 1.0
        self.newWidth = 1.0
        self.newHeight = 1.0

    def pointInLevelSpace(self, x, y):
        return x - self.newWidth/2, -y + self.newHeight/2
        
    def keepOnlyXY(self):
        """ keep only x and y from the (cmd, values) in vertex
        """
        newBlocks = []
        for vertex in self.blocks:
            vertex = [(values['x'], values['y']) for cmd, values in vertex]
            newBlocks.append(vertex)

        self.blocks = newBlocks

    def transform(self):
        newBlocks = []
        for vertex in self.blocks:
            if self.matrix is not None:
                # apply transform
                vertex = [self.matrix.applyOnPoint(x, y) for x, y in vertex]
            # apply ratio
            vertex = [(x * self.ratio, y * self.ratio) for x, y in vertex]

            newBlocks.append(vertex)

        self.blocks = newBlocks

    def addToAABB(self):
        for vertex in self.blocks:
            # add point to the aabb
            [self.aabb.addPoint(x, y) for x, y in vertex]

    def preProcessVertex(self):
        """ apply transformations on block vertex
            and add them to the bounding box of the block """
        self.blocks = Factory().create('path_parser').parse(self.pathsInfos)
        self.keepOnlyXY()
        self.transform()
        self.addToAABB()

    def addElementParams(self):
        for key, value in self.infos.iteritems():
            if type(value) == dict:
                if key.startswith('_'):
                    continue
                elif key == 'param':
                    for key, value in value.iteritems():
                        line = "\t\t<param name=\"%s\" value=\"%s\"/>"
                        self.content.append(line % (key, value))
                else:
                    xmlLine = "\t\t<%s" % key
                    for key, value in value.iteritems():
                        if key.startswith('_'):
                            continue
                        xmlLine += " %s=\"%s\"" % (key, value)
                    xmlLine += "/>"
                    self.content.append(xmlLine)
