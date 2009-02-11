from transform import Transform
from matrix import Matrix
from path import Path
from svgnode import rectAttrsToPathAttrs
import logging

class Layer:
    def __init__(self, attrs, matrix):
        self.attrs = attrs
        self.paths = []
        self.children = []
        self.unused = False
        self.matrix = Matrix()

        if 'transform' in self.attrs:
            self.matrix = Transform().createMatrix(self.attrs['transform'])

        if matrix is not None:
            self.addParentTransform(matrix)

        logging.debug("layer [%s] matrix=%s" % (self.attrs['id'], self.matrix))

    def addPath(self, attrs):
        self.paths.append(Path(attrs, self.matrix))

    def addRect(self, attrs):
        attrs = rectAttrsToPathAttrs(attrs)
        self.paths.append(Path(attrs, self.matrix))

    def addChild(self, childLayer):
        self.children.append(childLayer)

    def addParentTransform(self, matrix):
        # parent transformation is applied before self transformation
        self.matrix = matrix * self.matrix
#
#    def __str__(self):
#        return ""
