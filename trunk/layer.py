from transform import Transform
from matrix import Matrix
from path import Path
import logging, log

class Layer:
    def __init__(self, layerAttributes):
        self.attributes = layerAttributes
        self.paths      = []
        self.children   = []
        self.transformMatrix = Matrix()

        if self.attributes.has_key('transform'):
            self.transformMatrix = Transform().createTransformationMatrix(self.attributes['transform'])

    def addPath(self, pathAttributes):
        self.paths.append(Path(pathAttributes, self.transformMatrix))
        
    def addRect(self, rectAttributes):
        rectAttributes = self.transformRectIntoPath(rectAttributes)
        self.paths.append(Path(rectAttributes, self.transformMatrix))

    def addChild(self, childLayer):
        childLayer.addParentTransform(self.transformMatrix)
        self.children.append(childLayer)

    def addParentTransform(self, parentTranformMatrix):
        # parent transformation is applied before self transformation
        self.transformMatrix = parentTranformMatrix * self.transformMatrix

    def transformRectIntoPath(self, attrs):
        # rect transformation into path: http://www.w3.org/TR/SVG/shapes.html#RectElement
        # the formulas from svg doesn't work with one rounded corner, so let's try the one from inskcape for that corner (file sp-rect.cpp)
        # inkscape use C (bezier curve) instead of A (elliptic arc)
        #        #define C1 0.554
        #        sp_curve_moveto(c, x + rx, y);
        #        if (rx < w2) sp_curve_lineto(c, x + w - rx, y);
        #        sp_curve_curveto(c, x + w - rx * (1 - C1), y,     x + w, y + ry * (1 - C1),       x + w, y + ry);
        #        if (ry < h2) sp_curve_lineto(c, x + w, y + h - ry);
        #        sp_curve_curveto(c, x + w, y + h - ry * (1 - C1),     x + w - rx * (1 - C1), y + h,       x + w - rx, y + h);
        #        if (rx < w2) sp_curve_lineto(c, x + rx, y + h);
        #        sp_curve_curveto(c, x + rx * (1 - C1), y + h,     x, y + h - ry * (1 - C1),       x, y + h - ry);
        #        if (ry < h2) sp_curve_lineto(c, x, y + ry);
        #        sp_curve_curveto(c, x, y + ry * (1 - C1),     x + rx * (1 - C1), y,       x + rx, y);

       width  = float(attrs['width'])
       height = float(attrs['height'])
       x      = float(attrs['x'])
       y      = float(attrs['y'])
       rx     = 0.0
       ry     = 0.0
       if 'rx' in attrs:
           rx = float(attrs['rx'])
       if 'ry' in attrs:
           ry = float(attrs['ry'])

       if width == 0 or height == 0:
           raise Exception('Rectangle %s has its width or its height equals to zero' % attrs['id'])

       if rx < 0.0 or ry < 0.0:
           raise Exception('Rectangle rx (%f) or ry (%f) is less than zero' % (rx, ry))

       if rx == 0.0:
           rx = ry
       if ry == 0.0:
           ry = rx
       if rx > width / 2.0:
           rx = width / 2.0
       if ry > height / 2.0:
           ry = height / 2.0

       if rx == 0.0 and ry == 0.0:
           d = "M %f,%f L %f,%f L %f,%f L %f,%f L %f,%f z" % (x,y, x+width,y, x+width,y+height, x,y+height, x,y)
       else:
           # this is the constant which allow to calcultate the bezier curve control points
           C1 = 0.554
           d = "M %f,%f L %f,%f C %f,%f %f,%f %f,%f L %f,%f A %f,%f %d %d,%d %f,%f L %f,%f A %f,%f %d %d,%d %f,%f L %f,%f A %f,%f %d %d,%d %f,%f z" % (x+rx,y,  x+width-rx,y,  x+width-rx*(1-C1),y, x+width,y+ry*(1-C1), x+width,y+ry,  x+width,y+height-ry,  rx,ry,0,0,1,x+width-rx,y+height,  x+rx,y+height,  rx,ry,0,0,1,x,y+height-ry,  x,y+ry,  rx,ry,0,0,1,x+rx,y)

       attrs['d'] = d
       
       return attrs
