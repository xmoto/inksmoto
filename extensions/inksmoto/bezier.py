from math    import sqrt, ceil
from bezmisc import bezierlength

class Point:
    def __init__(self, point):
        self.x = point[0]
        self.y = point[1]

class Bezier:
    """ inspired from bezmisc inkscape extension by Aaron Spike """
    def __init__(self, bezierCurve):
        self.curve = bezierCurve
        self.point1        = Point(bezierCurve[0])
        self.controlPoint1 = Point(bezierCurve[1])
        self.controlPoint2 = Point(bezierCurve[2])
        self.point2        = Point(bezierCurve[3])
        
        self.x0 = self.point1.x
        self.y0 = self.point1.y
        self.cx = 3 * (self.controlPoint1.x - self.x0)
        self.cy = 3 * (self.controlPoint1.y - self.y0)
        self.bx = 3 * (self.controlPoint2.x - self.controlPoint1.x) - self.cx
        self.by = 3 * (self.controlPoint2.y - self.controlPoint1.y) - self.cy
        self.ax = self.point2.x - self.x0 - self.cx - self.bx
        self.ay = self.point2.y - self.y0 - self.cy - self.by

    def pointAt(self, t=0.5):
        x = self.ax * (t**3) + self.bx * (t**2) + self.cx * t + self.x0
        y = self.ay * (t**3) + self.by * (t**2) + self.cy * t + self.y0
        return x, y
    
    def approxLength(self):
        """ not the real lenght. """
        return sqrt(  (3*self.ax + 2*self.by + self.cx)**2
                    + (3*self.ay + 2*self.by + self.cy)**2)

    def realLength(self):
        return bezierlength(self.curve)

    def splitCurve(self, maxSegmentLength=1.0):
        result = []
        length = self.realLength()
        if length > maxSegmentLength:
            splits = int(ceil(length / maxSegmentLength))
            for step in xrange(1, splits+1):
                x, y = self.pointAt(step * 1.0/splits)
                result.append(['L', {'x': x, 'y': y}])
        else:
            result.append(['L', {'x': self.point2.x, 'y': self.point2.y}])
        return result
