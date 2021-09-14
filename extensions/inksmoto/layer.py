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

import logging
from .transform import Transform
from .matrix import Matrix
from .path import Path
from .svgnode import rectAttrsToPathAttrs
from .inkex import addNS

class Layer:
    def __init__(self, attrs, matrix):
        self.attrs = attrs
        self.paths = []
        self.children = []
        self.unused = False
        self.matrix = Matrix()

        if 'transform' in self.attrs:
            self.matrix = Transform().createMatrix(self.attrs['transform'])

        if matrix is not None:
            self.addParentTransform(matrix)

        logging.debug("layer [%s] matrix=%s" % (self.attrs['id'], self.matrix))

    def add(self, node):
        if node.tag == addNS('path', 'svg'):
            self.addPath(node.attrib)
        elif block.tag == addNS('rect', 'svg'):
            self.addRect(node.attrib)

    def addPath(self, attrs):
        self.paths.append(Path(attrs, self.matrix))

    def addRect(self, attrs):
        attrs = rectAttrsToPathAttrs(attrs)
        self.paths.append(Path(attrs, self.matrix))

    def addChild(self, childLayer):
        self.children.append(childLayer)

    def addParentTransform(self, matrix):
        # parent transformation is applied before self transformation
        self.matrix = matrix * self.matrix
