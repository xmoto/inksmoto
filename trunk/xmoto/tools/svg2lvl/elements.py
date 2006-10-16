from factory import Factory
import logging, log

class Element:
    def __init__(self, *args, **keywords):
        self.id                  = keywords['id']
        self.elementInformations = keywords['elementInformations']
        self.vertex              = keywords['vertex']
        self.transformMatrix     = keywords['transformMatrix']
        self.content = []
        self.initBoundingBox()

    def applyRatioAndTransformOnPoint(self, x, y):
        x, y = self.transformMatrix.applyOnPoint(x, y)
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
                self.addVerticeToBoundingBox(x, y)

    def pointInLevelSpace(self, x, y):
        x =  x - self.newWidth/2
        y = -y + self.newHeight/2
        return x, y
        
    def addVerticeToBoundingBox(self, x, y):
        if x > self.maxX:
            self.maxX = x
        if x < self.minX:
            self.minX = x
        if y > self.maxY:
            self.maxY = y
        if y < self.minY:
            self.minY = y

    def initBoundingBox(self):
        self.minX = 99999
        self.maxX = -99999
        self.minY = 99999
        self.maxY = -99999
                
    def addElementParams(self):
        for key,value in self.elementInformations.iteritems():
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
