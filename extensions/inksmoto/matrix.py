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

from math import cos, sin, tan

def identity():
    return Matrix([[1, 0, 0],
                   [0, 1, 0],
                   [0, 0, 1]])
def zero():
    return Matrix([[0, 0, 0],
                   [0, 0, 0],
                   [0, 0, 0]])

def translate(tx, ty):
    return Matrix([[1, 0, tx],
                   [0, 1, ty],
                   [0, 0, 1]])

def scale(sx, sy):
    return Matrix([[sx, 0,  0],
                   [0,  sy, 0],
                   [0,  0,  1]])

def rotate(angle):
    return Matrix([[cos(angle), -sin(angle), 0],
                   [sin(angle), cos(angle),  0],
                   [0,          0,           1]])

def skewX(angle):
    return Matrix([[1, tan(angle), 0],
                   [0, 1,          0],
                   [0, 0,          1]])

def skewY(angle):
    return Matrix([[1,          0, 0],
                   [tan(angle), 1, 0],
                   [0,          0, 1]])

class Matrix:
    """ see http://www.yoyodesign.org/doc/w3c/svg1/coords.html for 
    the equivalence between transformations and matrix
    """
    def __init__(self, *args):
        if len(args) == 0:
            self.matrix = identity().matrix
        else:
            # assume the input is good
            self.matrix = args[0]
    
    def add_translate(self, *args):
        if len(args) == 1:
            tx = args[0]
            ty = 0.0
        else:
            tx = args[0]
            ty = args[1]

        return self * translate(float(tx), float(ty))

    def add_scale(self, *args):
        if len(args) == 1:
            sx = args[0]
            sy = 0.0
        else:
            sx = args[0]
            sy = args[1]

        return self * scale(sx, sy)

    def add_rotate(self, *args):
        if len(args) == 1:
            angle = args[0]
            return self * rotate(angle)
        else:
            # translate(<cx>, <cy>)
            # rotate(<angle-rotation>)
            # translate(-<cx>, -<cy>)
            angle = args[0]
            cx    = args[1]
            cy    = args[2]

            matrix = translate(cx, cy) * rotate(angle)
            matrix = matrix * translate(-cx, -cy)
            return self * matrix

    def add_skewX(self, angle):
        return self * skewX(angle)

    def add_skewY(self, angle):
        return self * skewY(angle)
    
    def add_matrix(self, m11, m21, m12, m22, m13, m23):
        return self * Matrix([[m11, m12, m13], [m21, m22, m23], [0, 0, 1]])

    def __mul__(self, b):
        result = zero().matrix

        if b == identity():
            return Matrix(self.matrix)
        elif self == identity():
            return Matrix(b.matrix)

        # not the classic row*col algorithm
        # TODO::profiling
        i = 0
        for aRow in self.matrix:
            for aValue, bRow  in zip(aRow, b.matrix):
                j = 0
                for bValue in bRow:
                    result[i][j] += aValue * bValue
                    j += 1
            i += 1

        return Matrix(result)

    def applyOnPoint(self, x, y):
        if self.matrix == identity():
            return x, y
        else:
            m = Matrix([[x], [y] , [1]])
            result = self * m
            x = result.matrix[0][0]
            y = result.matrix[1][0]
            
            return x, y
    
    def partialApplyOnPoint(self, x, y):
        if self == identity():
            return x, y
        else:
            m = Matrix([[x], [y], [1]])
            partial = Matrix([[self.matrix[0][0], self.matrix[0][1], 0],
                              [self.matrix[1][0], self.matrix[1][1], 0],
                              [0, 0, 1]])
            result = partial * m
            x = result.matrix[0][0]
            y = result.matrix[1][0]
            
            return x, y
        
    def error_add(self):
        # TODO::error checking ?
        pass

    def __str__(self):
        return str(self.matrix)

    def createTransform(self):
        return ['matrix', 6,
                self.matrix[0][0], self.matrix[1][0],
                self.matrix[0][1], self.matrix[1][1],
                self.matrix[0][2], self.matrix[1][2]]
