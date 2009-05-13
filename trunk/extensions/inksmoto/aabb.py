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

""" A simple aabb. Can apply a transform on it """

from transform import Transform
from bezier import Bezier
from parametricArc import ParametricArc

class AABB:
    """ Axis aligned bounding box """
    def __init__(self):
        self.reinit()

    def reinit(self):
        inf = 1e500
        self.xmin = inf
        self.xmax = -inf
        self.ymin = inf
        self.ymax = -inf

    def addPoint(self, x, y):
        if x < self.xmin:
            self.xmin = x
        if x > self.xmax:
            self.xmax = x
        if y < self.ymin:
            self.ymin = y
        if y > self.ymax:
            self.ymax = y

    def width(self):
        return self.xmax - self.xmin

    def height(self):
        return self.ymax - self.ymin

    def x(self):
        return self.xmin

    def y(self):
        return self.ymin

    def cx(self):
        return (self.xmin + self.xmax)/2.0

    def cy(self):
        return (self.ymin + self.ymax)/2.0

    def applyTransform(self, transform):
        matrix = Transform().createMatrix(transform)
        (x1, y1) = matrix.applyOnPoint(self.xmin, self.ymin)
        (x2, y2) = matrix.applyOnPoint(self.xmax, self.ymax)
        self.reinit()
        self.addPoint(x1, y1)
        self.addPoint(x2, y2)

    def addBezier(self, (lastX, lastY), params):
        x1, y1 = params['x1'], params['y1']
        x2, y2 = params['x2'], params['y2']
        x,  y  = params['x'],  params['y']
        bezVer = Bezier(((lastX, lastY), (x1, y1), (x2, y2), (x, y))).splitCurve()
        for cmd, values in bezVer:
            self.addPoint(values['x'], values['y'])

    def addArc(self, (lastX, lastY), params):
        x,  y  = params['x'],  params['y']
        rx, ry = params['rx'], params['ry']
        arcVer = ParametricArc((lastX, lastY), (x, y), (rx, ry),
                               params['x_axis_rotation'], 
                               params['large_arc_flag'], 
                               params['sweep_flag']).splitArc()
        for cmd, values in arcVer:
            self.addPoint(values['x'], values['y'])
