from math import cos, sin, tan
import logging, log

class Matrix:
    """ see http://www.yoyodesign.org/doc/w3c/svg1/coords.html for 
    the equivalence between transformations and matrix
    """
    def __init__(self, *args):
        if len(args) == 0:
            self.matrix = self.identity()
        else:
            # assume the input is good
            self.matrix = args[0]
    
    def identity(self):
        return [[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]]
    def zero(self):
        return [[0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]]

    def translate(self, tx, ty):
        return [[1, 0, tx],
                [0, 1, ty],
                [0, 0, 1]]

    def scale(self, sx, sy):
        return [[sx, 0,  0],
                [0,  sy, 0],
                [0,  0,  1]]

    def rotate(self, angle):
        return [[cos(angle), -sin(angle), 0],
                [sin(angle), cos(angle),  0],
                [0,          0,           1]]

    def skewX(self, angle):
        return [[1, tan(angle), 0],
                [0, 1,          0],
                [0, 0,          1]]

    def skewY(self, angle):
        return [[1,          0, 0],
                [tan(angle), 1, 0],
                [0,          0, 1]]

    def add_translate(self, *args):
        if len(args) == 1:
            tx = args[0]
            ty = 0.0
        else:
            tx = args[0]
            ty = args[1]

        return self * Matrix(self.translate(float(tx), float(ty)))

    def add_scale(self, *args):
        if len(args) == 1:
            sx = args[0]
            sy = 0.0
        else:
            sx = args[0]
            sy = args[1]

        return self * Matrix(self.scale(sx, sy))

    def add_rotate(self, *args):
        if len(args) == 1:
            angle = args[0]
            return self * Matrix(self.rotate(angle))
        else:
            # translate(<cx>, <cy>) rotate(<angle-rotation>) translate(-<cx>, -<cy>)
            angle = args[0]
            cx    = args[1]
            cy    = args[2]

            matrix = Matrix(self.translate(cx, cy)) * Matrix(self.rotate(angle))
            matrix = matrix * Matrix(self.translate(-cx, -cy))
            return self * matrix

    def add_skewX(self, angle):
        return self * Matrix(self.skewX(angle))

    def add_skewY(self, angle):
        return self * Matrix(self.skewY(angle))
    
    def add_matrix(self, m11, m21, m12, m22, m13, m23):
        return self * Matrix([[m11, m12, m13], [m21, m22, m23], [0, 0, 1]])

    def __mul__(self, B):
        result = self.zero()

        if B.matrix == self.identity():
            return Matrix(self.matrix)
        elif self.matrix == self.identity():
            return Matrix(B.matrix)

        # not the classic row*col algorithm
        # TODO::profiling
        i = 0
        for Arow in self.matrix:
            for Avalue, Brow  in zip(Arow, B.matrix):
                j = 0
                for Bvalue in Brow:
                    result[i][j] += Avalue * Bvalue
                    j += 1
            i += 1

        return Matrix(result)

    def applyOnPoint(self, x, y):
        if self.matrix == self.identity():
            return x, y
        else:
            m = Matrix([[x], [y] , [1]])
            result = self * m
            x = result.matrix[0][0]
            y = result.matrix[1][0]
            
            return x, y
    
    def partialApplyOnPoint(self, x, y):
        if self.matrix == self.identity():
            return x, y
        else:
            m = Matrix([[x], [y], [1]])
            partial = Matrix([[self.matrix[0][0], self.matrix[0][1], 0], [self.matrix[1][0], self.matrix[1][1], 0], [0,0,1]])
            result = partial * m
            x = result.matrix[0][0]
            y = result.matrix[1][0]
            
            return x, y
        
    def error_add(self):
        # TODO::error checking ?
        pass

    def __str__(self):
        return str(self.matrix)
