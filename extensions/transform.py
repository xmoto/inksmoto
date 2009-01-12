from singleton import Singleton
from factory   import Factory
from matrix    import Matrix
import logging, log

class Transform:
    __metaclass__ = Singleton
    
    def __init__(self):
        self.parser = Factory().createObject('transform_parser')

    def createTransformationMatrix(self, transforms):
        matrix = Matrix()

        transformElements = self.parser.parse(transforms)
        
        while len(transformElements) > 0:
            transform = transformElements.pop(0)
            nbParam   = transformElements.pop(0)
            params    = []
            for i in xrange(nbParam):
                params.append(transformElements.pop(0))
             
            function = getattr(matrix, 'add_'+transform, matrix.error_add)
            matrix = function(*params)

        return matrix        

