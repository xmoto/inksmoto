from math import sqrt, acos
import logging, log

class Vector:
    def __init__(self, *args):
        nbArgs = len(args)
        if nbArgs == 0:
            self.vector = [0, 0]
        elif nbArgs == 1:
            self.vector = args[0]
        elif nbArgs == 2:
            self.vector = [args[0], args[1]]
        else:
            raise Exception("Vector::__init__::wrong parameters: %s" % (str(args)))
        
    def length(self):
        return sqrt(self.vector[0]*self.vector[0] + self.vector[1]*self.vector[1])
    
    def dot(self, v):
        result = 0.0
        for x,y in zip(self.vector, v.vector):
            result += x * y
        return result

    def angle(self, v):
        length = self.length()*v.length()
        if length == 0.0:
            return 0.0
        cosa = self.dot(v)/length
        # bound it to [-1, 1]
        cosa = max(-1., min(1.,cosa))
        return acos(cosa)

    def __str__(self):
        return str(self.vector)
