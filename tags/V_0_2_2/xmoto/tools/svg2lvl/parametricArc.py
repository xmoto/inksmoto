from vector import Vector
import math

class ParametricArc:
    def __init__(self, (x1, y1), (x2, y2), (rx, ry), x_rot, fA, fS):
        # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        if rx == 0.0 or ry == 0.0:
            self.ok = False
            return
        else:
            self.ok = True
        
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.rx, self.ry = rx, ry
        
        x1p = (x1-x2)/2
        y1p = (y1-y2)/2

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
        
        self.cx = cxp + (x1+x2)/2
        self.cy = cyp + (y1+y2)/2
        
        v1 = Vector(1, 0)
        v2 = Vector((x1p-cxp)/rx,  (y1p-cyp)/ry)
        v3 = Vector((-x1p-cxp)/rx, (-y1p-cyp)/ry)
        
        self.theta1 = v1.angle(v2)
        self.deltaTheta = v2.angle(v3)
        
        if fS == 0 and self.deltaTheta > 0:
            self.deltaTheta -= 2*math.pi
        if fS == 1 and self.deltaTheta < 0:
            self.deltaTheta += 2*math.pi

    def pointAt(self, angle):
        return (self.rx*math.cos(angle) + self.cx, self.ry*math.sin(angle) + self.cy)
    
    def splitArc(self, maxSegmentLength):
        if not self.ok:
            return []
        
        result = []
        
        angle = self.theta1
        limit = self.theta1 + self.deltaTheta
        step  = math.pi/50.0
        if self.deltaTheta < 0:
            while(angle > limit):
                x, y = self.pointAt(angle)
                result.append(['L', {'x': x, 'y': y}])
                angle -= step
        else:
            while(angle < limit):
                x, y = self.pointAt(angle)
                result.append(['L', {'x': x, 'y': y}])
                angle += step
        return result
