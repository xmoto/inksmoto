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

from .vector import Vector
import math

class ParametricArc:
    def __init__(self, xxx_todo_changeme, xxx_todo_changeme1, xxx_todo_changeme2, x_rot, fA, fS):
        # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        (x1, y1) = xxx_todo_changeme
        (x2, y2) = xxx_todo_changeme1
        (rx, ry) = xxx_todo_changeme2
        if rx == 0.0 or ry == 0.0:
            self.ok = False
            return
        else:
            self.ok = True

        x1p = (x1-x2)/2
        y1p = (y1-y2)/2

        # Correction of out-of-range radii
        # http://www.w3.org/TR/SVG/implnote.html#ArcCorrectionOutOfRangeRadii
        d = (x1p**2)/(rx**2) + (y1p**2)/(ry**2)
        if d > 1.0:
            sqrt_d = math.sqrt(d)
            rx = sqrt_d * rx
            ry = sqrt_d * ry

        # you can have up=-0.000000, so we abs it
        up   = abs(rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2)
        down = rx**2 * y1p**2 + ry**2 * x1p**2
        if down == 0.0:
            coeff = 0
        else:
            coeff = math.sqrt(up/down)

        if fA == fS:
            coeff = -coeff

        cxp = coeff * rx * y1p / ry
        cyp = coeff * -ry * x1p / rx

        v1 = Vector(1, 0)
        v2 = Vector((x1p-cxp)/rx,  (y1p-cyp)/ry)
        v3 = Vector((-x1p-cxp)/rx, (-y1p-cyp)/ry)

        self.theta1 = v1.angle(v2)
        self.deltaTheta = v2.angle(v3)

        # when abs(delta theta) is under the limit there's angle problems
        limit = 0.01

        if (fS == 0
            and (self.deltaTheta > 0 or math.fabs(self.deltaTheta) < limit)):
            self.deltaTheta -= 2*math.pi
        if (fS == 1
            and (self.deltaTheta < 0 or math.fabs(self.deltaTheta) < limit)):
            self.deltaTheta += 2*math.pi

        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.rx, self.ry = rx, ry
        self.cx = cxp + (x1+x2)/2
        self.cy = cyp + (y1+y2)/2

    def pointAt(self, angle):
        return (self.rx*math.cos(angle) + self.cx,
                self.ry*math.sin(angle) + self.cy)

    def splitArc(self):
        if not self.ok:
            return []

        result = []

        angle = self.theta1
        limit = self.theta1 + self.deltaTheta
        step  = math.pi/50.0

        if self.deltaTheta < 0:
            while(angle > limit):
                x, y = self.pointAt(angle)
                result.append((x, y))
                angle -= step
        else:
            while(angle < limit):
                x, y = self.pointAt(angle)
                result.append((x, y))
                angle += step

        return result
