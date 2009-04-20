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

from factory import Factory
from aabb import AABB

class Element:
    def __init__(self, **kwargs):
        self._id = kwargs['_id']
        self.infos = kwargs['infos']
        self.vertex = kwargs['vertex']
        if 'matrix' in kwargs:
            self.matrix = kwargs['matrix']
        else:
            self.matrix = None
        self.content = []
        self.aabb = AABB()

        # added by writeContent
        self.ratio = 1.0
        self.newWidth = 1.0
        self.newHeight = 1.0

    def applyRatioAndTransformOnPoint(self, x, y):
        if self.matrix is not None:
            x, y = self.matrix.applyOnPoint(x, y)
        return self.applyRatioOnPoint(x, y)
    
    def applyRatioOnPoint(self, x, y):
        return x * self.ratio, y * self.ratio

    def preProcessVertex(self):
        """ apply transformations on block vertex
            and add them to the bounding box of the block """
        self.vertex = Factory().createObject('path_parser').parse(self.vertex)
        for cmd, values in self.vertex:
            if cmd != 'Z':
                x, y = self.applyRatioAndTransformOnPoint(values['x'],
                                                          values['y'])
                values['x'] = x
                values['y'] = y
                self.aabb.addPoint(x, y)

    def pointInLevelSpace(self, x, y):
        x =  x - self.newWidth/2
        y = -y + self.newHeight/2
        return x, y
        
    def addElementParams(self):
        for key, value in self.infos.iteritems():
            if type(value) == dict:
                if key == 'param':
                    for key, value in value.iteritems():
                        line = "\t\t<param name=\"%s\" value=\"%s\"/>"
                        self.content.append(line % (key, value))
                else:
                    xmlLine = "\t\t<%s" % key
                    for key, value in value.iteritems():
                        xmlLine += " %s=\"%s\"" % (key, value)
                    xmlLine += "/>"
                    self.content.append(xmlLine)
