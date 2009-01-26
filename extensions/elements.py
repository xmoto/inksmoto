from factory import Factory
from aabb import AABB
import logging, log

class Element:
    def __init__(self, *args, **kwargs):
        self.id = kwargs['id']
        self.infos = kwargs['infos']
        self.input = kwargs['input']
        self.vertex = kwargs['vertex']
        if 'transformMatrix' in kwargs:
            self.matrix = kwargs['transformMatrix']
        else:
            self.matrix = None
        self.content = []
        self.aabb = AABB()

    def applyRatioAndTransformOnPoint(self, x, y):
        if self.matrix is not None:
            x, y = self.matrix.applyOnPoint(x, y)
        return self.applyRatioOnPoint(x, y)
    
    def applyRatioOnPoint(self, x, y):
        return x * self.ratio, y * self.ratio

    def preProcessVertex(self):
        # apply transformations on block vertex
        # and add them to the bounding box of the block
        self.vertex = Factory().createObject('path_parser').parse(self.vertex)
        for element, valuesDic in self.vertex:
            if element != 'Z':
                x, y = self.applyRatioAndTransformOnPoint(valuesDic['x'], valuesDic['y'])
                valuesDic['x'] = x
                valuesDic['y'] = y
                self.aabb.addPoint(x, y)

    def pointInLevelSpace(self, x, y):
        x =  x - self.newWidth/2
        y = -y + self.newHeight/2
        return x, y
        
    def addElementParams(self):
        for key,value in self.infos.iteritems():
            if type(value) == dict:
                if key == 'param':
                    for key,value in value.iteritems():
                        self.content.append("\t\t<param name=\"%s\" value=\"%s\"/>" % (key, value))
                else:
                    xmlLine = "\t\t<%s" % key
                    for key,value in value.iteritems():
                        xmlLine += " %s=\"%s\"" % (key, value)
                    xmlLine += "/>"
                    self.content.append(xmlLine)
