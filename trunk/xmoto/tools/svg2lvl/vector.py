from Numeric import array, dot
from math    import sqrt, acos
import logging, log

class Vector:
    def __init__(self, *args):
        nbArgs = len(args)
        if nbArgs == 0:
            self.vector = array([0, 0])
        elif nbArgs == 1:
            self.vector = array(args[0])
        elif nbArgs == 2:
            self.vector = array([args[0], args[1]])
        else:
            raise Exception("Vector::__init__::wrong parameters: %s" % (str(args)))
        
    def length(self):
        return sqrt(self.vector[0]*self.vector[0] + self.vector[1]*self.vector[1])
    
    def dot(self, v):
        return dot(self.vector, v.vector)

    def angle(self, v):
        #cosa = self.dot(v)/(self.length()*v.length())
        #return acos(cosa)

        dot_value = self.dot(v)
        lengths = self.length()*v.length()
        cosa = dot_value / lengths
        # bound it to [-1, 1]
        cosa = max(-1., min(1.,cosa))
        
        logging.debug("dot: %f lengths: %f cosa: %f" % (dot_value, lengths, cosa))

        angle = acos(cosa)
        return angle
        


    def __str__(self):
        return str(self.vector)
