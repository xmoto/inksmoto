#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import log, logging
import base64
from transform import Transform
from factory   import Factory
from aabb import AABB
from lxml import etree
from inkex import addNS
from xmotoTools import getExistingImageFullPath, getValue
from lxml.etree import Element
from availableElements import AvailableElements
from matrix import Matrix
from vector import Vector
from confGenerator import Conf
ENTITY_RADIUS = Conf()['ENTITY_RADIUS']
SVG2LVL_RATIO = Conf()['SVG2LVL_RATIO']

def convertToXmNode(node, svg=None):
    # node is not a new-style class, so this doesn't work:
    #node.__class__ = XmNode
    # -> add all the XmNode methods to node
    #
    # this doesn't work either:
    #    xmnode = XmNode()
    #    for attribute in dir(xmnode):
    #        if attribute.startswith('_'):
    #            continue
    #        setattr(node, attribute, getattr(xmnode, attribute))
    #
    #    node.svg = svg
    if isXmNode(node) == True:
        if node.svg is None:
            node.svg = svg
        return node
    else:
        return XmNode(node, svg)

def isXmNode(node):
    return hasattr(node, '_node')

def createNewNode(parentNode, _id, tag, svg=None):
    if isXmNode(parentNode):
        parentNode = parentNode._node

    newNode = etree.SubElement(parentNode, tag)
    if _id is not None:
        newNode.set('id', _id)
    return convertToXmNode(newNode, svg)

class XmNode:
    BLOCK=1
    BITMAP=2

    def __init__(self, node, svg=None):
        self._node = node
        self.svg = svg

    # we keep the Element node as a member of XmNode, but we still
    # want to be able to use the Element methods and attributes with
    # the XmNode, so we intercept set and get to redirect them to the
    # Element's ones
    def __getattr__(self, name):
        if '_node' in self.__dict__ and hasattr(self._node, name):
            return getattr(self._node, name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            return None

    def __setattr__(self, name, value):
        if name in ['_node', 'svg']:
            self.__dict__[name] = value
        else:
            if hasattr(self._node, name):
                setattr(self._node, name, value)
            else:
                setattr(self, name, value)

    def translate(self, x, y):
        transform = self.get('transform', default='')
        matrix = Transform().createMatrix(transform)
        matrix = matrix.add_translate(x, y)
        parser = Factory().create('transform_parser')
        transform = parser.unparse(matrix.createTransform())
        self.set('transform', transform)

    def duplicate(self, newId):
        parentNode = self.getparent()
        newNode = createNewNode(parentNode, newId, self.tag, self.svg)
        for key, value in self.items():
            if self.checkNamespace(key) == False:
                newNode.set(key, value)
        newNode.set('id', newId)
        return newNode

    def setStyleLabel(self, label, style):
        self.set(addNS('xmoto_label', 'xmoto'), label)
        self.set('style', style)

    def getAABB(self):
        aabb = AABB()

        lastX = 0
        lastY = 0

        # to acces values with simplepath format
        (x, y) = range(-2, 0)

        if self.tag == addNS('path', 'svg'):
            blocks = Factory().create('path_parser').parse(self.get('d'))
            for vertex in blocks:
                for (cmd, values) in vertex:
                    if values is not None:
                        if cmd == 'C':
                            aabb.addBezier((lastX, lastY), values)
                        elif cmd == 'A':
                            aabb.addArc((lastX, lastY), values)
                        else:
                            aabb.addPoint(values[x], values[y])

                        lastX = values[x]
                        lastY = values[y]

        elif self.tag in [addNS('rect', 'svg'), addNS('image', 'svg')]:
            x = float(self.get('x'))
            y = float(self.get('y'))
            width  = float(self.get('width'))
            height = float(self.get('height'))
            aabb.addPoint(x, y)
            aabb.addPoint(x + width, y + height)

        elif self.tag == addNS('use', 'svg'):
            x = float(self.get('x'))
            y = float(self.get('y'))
            # the first character of an href is a #
            imageId = self.get(addNS('href', 'xlink'))[1:]
            image = self.svg.getImage(imageId)
            width = float(image.get('width'))
            height = float(image.get('height'))
            aabb.addPoint(x, y)
            aabb.addPoint(x + width, y + height)

        else:
            raise Exception("Can't get AABB of a node which is neither a path \
    nor a rect.\nnode tag:%s" % self.tag)

        return aabb

    def newParent(self, new):
        """ to set a new parent for a node, there's no need to remove it
        from it's old parent
        """
        new.append(self._node)

    def subLayerElementToSingleNode(self):
        if self.isSubLayer() == True:
            aabb = self.getCircleChild().getAABB()
            self.deleteChildren()
            id_ = self.get('id', '')
            pos = id_.find('g_')
            if pos != -1:
                id_ = id_[pos+2:]
                self.set('id', id_)
            return (self, aabb)
        else:
            parent = convertToXmNode(self.getparent())
            if parent.isSubLayer() == True:
                return parent.subLayerElementToSingleNode()
            else:
                return (self, None)

    def getParsedLabel(self):
        label = self.get(addNS('xmoto_label', 'xmoto'), '')
        parser = Factory().create('label_parser')
        return parser.parse(label)

    def checkNamespace(self, attrib):
        pos1 = attrib.find('{')
        pos2 = attrib.find('}')
        if pos1 != -1 and pos2 != -1:
            namespace = attrib[pos1+1:pos2]
            if ('inkscape' in self.nsmap and namespace in self.nsmap['inkscape']
                or 'sodipodi' in self.nsmap and namespace in self.nsmap['sodipodi']):
                return True
        return False

    def removeInkscapeAttribute(self):
        # if you only change the 'd' attribute the shape won't be
        # update in inkscape as inkscape uses it's own attributes
        for key in self.attrib.keys():
            if self.checkNamespace(key) == True:
                del self.attrib[key]

    def belongsToSubLayer(self):
        return convertToXmNode(self.getparent()).isSubLayer()

    def isSubLayer(self, type=None):
        """ a sub-layer has an xmoto_label
        """
        if self.tag == addNS('g', 'svg'):
            label =  self.get(addNS('xmoto_label', 'xmoto'), '')
            if label == '':
                return False
            if type is None:
                return True
            elif type == XmNode.BITMAP:
                (g, circle, use) = self.getImageNodes(testOnly=True)
                return (g is not None and circle is not None and use is not None)
            elif type == XmNode.BLOCK:
                return self.haveColoredBlocksChildren()
        else:
            return False

    def deleteChildren(self):
        for child in self.getchildren():
            self.remove(child)

    def transform(self, rotation, reversed_, (tx, ty)):
        matrix = Matrix()
        if 'transform' in self.attrib:
            del self.attrib['transform']

        # translate around the origin, do the transfroms
        # then translate back.
        matrix = matrix.add_translate(tx, ty)

        if rotation != 0.0:
            matrix = matrix.add_rotate(-rotation)
        if reversed_ == True:
            matrix = matrix.add_scale(-1, 1)

        matrix = matrix.add_translate(-tx, -ty)

        if matrix != Matrix():
            parser = Factory().create('transform_parser')
            transform = parser.unparse(matrix.createTransform())
            self.set('transform', transform)

    def setNodeAsCircle(self, r, aabb=None):
        if aabb is None:
            aabb = self.getAABB()

        if self.tag == addNS('rect', 'svg'):
            self.tag = addNS('path', 'svg')

        self.set('d', getCenteredCircleSvgPath(aabb.cx(), aabb.cy(), r))
        self.removeInkscapeAttribute()

    def setNodeAsRectangle(self, aabb=None):
        if aabb is None:
            aabb = self.getAABB()

        if self.tag != addNS('rect', 'svg'):
            self.tag = addNS('rect', 'svg')
            if 'd' in self.attrib:
                del self.attrib['d']

        self.set('x', str(aabb.x()))
        self.set('y', str(aabb.y()))
        self.set('width', str(aabb.width()))
        self.set('height', str(aabb.height()))
        self.removeInkscapeAttribute()

    def haveColoredBlocksChildren(self):
        if len(self.getchildren()) != 2:
            return False
        for child in self.getchildren():
            label = child.get(addNS('xmoto_label', 'xmoto'), '')
            parser = Factory().create('label_parser')
            label = parser.parse(label)
            if 'typeid' in label:
                # only entities have a typeid
                return False
        return True

    def addColoredChildren(self, node, label, style, coloredStyle):
        nbChildren = len(self.getchildren())
        if nbChildren == 2:
            self.getchildren()[0].set('style', coloredStyle)
            self.getchildren()[1].set('style', style)
        elif nbChildren == 1:
            colored = node.duplicate(node.get('id')+'colored')
            colored.set('style', coloredStyle)
            # the colored block has to be under the textured one
            self.insert(0, colored._node)
        else:
            log.outMsg("The sublayer %s has a wrong number of \
children: %d" % (self.get('id', ''), nbChildren))

    def removeColoredChildren(self, label, style):
        """ in the svg, replace self (the g node) by its textured
        child
        """
        parent = self.getparent()
        coloredChild = self.getchildren()[0]
        texturedChild = convertToXmNode(self.getchildren()[1])
        texturedChild.newParent(parent)
        texturedChild.setStyleLabel(label, style)
        self.clear()
        parent.remove(self._node)

    def getSubLayerNode(self, testOnly=False):
        """ returns the sublayer node of a node.
        create it if it doesn't exist yet.
        """
        if self.tag != addNS('g', 'svg'):
            # the user selected a subelement instead of the
            # sublayer or the node is not a sublayer yet
            parent = convertToXmNode(self.getparent())
            if parent.isSubLayer() == True:
                g = parent
            else:
                if testOnly == False:
                    g = createNewNode(parent,
                                      'g_' + self.get('id', ''),
                                      addNS('g', 'svg'))
                    g.set(addNS('xmoto_label', 'xmoto'),
                          self.get(addNS('xmoto_label', 'xmoto'), ''))
                    self.newParent(g)
                else:
                    return None
        else:
            g = self

        return convertToXmNode(g, self.svg)

    def getImageNodes(self, testOnly=False):
        """ an image is made a of sublayer with two children:
        a circle
        an image (with a use node)
        """
        g = self.getSubLayerNode(testOnly)

        if g is None:
            return (None, None, None)

        try:
            circle = g.getCircleChild()
        except Exception, e:
            _id = g.get('id', '')

            logging.warning("Sprite [%s] is an empty layer. \
Let's delete it\n%s" % (_id, e))
            parent = g.getparent()
            parent.remove(g)
            return (None, None, None)

        use = g.find(addNS('use', 'svg'))
        if use is None:
            # deprecated, we no longer use images, uses instead
            image  = g.find(addNS('image', 'svg'))
            if image is not None:
                g.remove(image)

        return (g, circle, use)

    def setNodeAsBitmap(self, svg, texName, radius, bitmaps, label, style,
                        scale=1.0, _reversed=False, rotation=0.0):
        if self.isSubLayer(type=self.BLOCK):
            # remove one of the two children
            children = self.getchildren()
            child = children[0]
            self.remove(self.getchildren()[0])

        (g, circle, use) = self.getImageNodes()

        if g is None:
            return

        # if the node has more than one circle, delete it
        circles = g.findall(addNS('path', 'svg'))
        if len(circles) > 1:
            for c in circles:
                if c == circle:
                    continue
                else:
                    g.remove(c)

        # set the xmoto_label on both the sublayer and the
        # circle (for backward compatibility)
        g.set(addNS('xmoto_label', 'xmoto'), label)

        circle.set(addNS('xmoto_label', 'xmoto'), label)
        circle.set('style', style)

        if g.get('style') is not None:
            del g.attrib['style']

        circle = convertToXmNode(circle, self.svg)
        circle.setNodeAsCircle(scale * radius)

        # set the circle transform to the layer
        transform = circle.get('transform')
        if transform is not None:
            g.set('transform', transform)
            del circle.attrib['transform']

        (x, y, cx, cy, width, height) = getImageDimensions(texName, scale,
                                                           circle.getAABB())

        imageId = svg.addImage(texName, bitmaps, width, height)

        if imageId is None:
            return

        if use is None:
            try:
                use = newUseNode('image_' + circle.get('id'),
                                 x, y, imageId)
                # insert the use as the first child so that
                # it get displayed before the circle in inkscape
                g.insert(0, use)
            except Exception, e:
                logging.info("Can't create image for sprite %s.\n%s"
                             % (texName, e))
        else:
            for name, value in [('x', str(x)),
                                ('y', str(y)),
                                (addNS('href', 'xlink'), '#'+imageId)]:
                use.set(name, value)

        if use is not None:
            use = convertToXmNode(use, self.svg)
            use.transform(rotation, _reversed, (cx, cy))

            # set the label on the image to check after a change
            # if the image need some change too
            use.set(addNS('saved_xmoto_label', 'xmoto'), label)

    def getCircleChild(self):
        """ for a sprite, there's a sublayer and inside it, a use node
        (pointing to the image) and a path node (the circle).  But it's
        possible that the user remove only the circle, so we have to
        recreate it (as a rectangle !)
        """
        circle = self.find(addNS('path', 'svg'))
        if circle is None:
            circle = self.find(addNS('rect', 'svg'))
            if circle is None:
                image = self.find(addNS('image', 'svg'))
                use = self.find(addNS('use', 'svg'))
                if (image is None and use is None):
                    raise Exception('The sprite object is neither a path, \
a rect, a use nor an image')
                else:
                    # the user deleted the circle, lets recreate it
                    if image is not None:
                        node = image
                    else:
                        node = use
                    node = convertToXmNode(node, self.svg)
                    aabb = node.getAABB()
                    _id = self.get('id', '')
                    pos = _id.find('g_')
                    if pos != -1:
                        _id = _id[pos+len('g_'):]
                    else:
                        _id = None
                    circle = createNewNode(self, _id, addNS('rect', 'svg'))
                    circle.setNodeAsRectangle(aabb)

        return convertToXmNode(circle, self.svg)

def getImageDimensions(texName, scale, aabb):
    infos = getValue(AvailableElements()['SPRITES'], texName)
    cx = float(getValue(infos,
                        'centerX',
                        default='0.5')) / SVG2LVL_RATIO
    cy = float(getValue(infos,
                        'centerY',
                        default='0.5')) / SVG2LVL_RATIO

    width  = float(getValue(infos,
                            'width',
                            default='1.0')) / SVG2LVL_RATIO
    height = float(getValue(infos,
                            'height',
                            default='1.0')) / SVG2LVL_RATIO
    scaledWidth = width
    scaledHeight = height

    if scale != 1.0:
        scaledWidth  = scale * width
        scaledHeight = scale * height

    cx += (scaledWidth - width) / 2.0
    cy += (scaledHeight - height) / 2.0

    x = aabb.cx() - cx
    # with the same coordinates, inkscape doesn't display
    # images at the same place as xmoto ...
    y = aabb.cy() - scaledHeight + cy

    return (x, y, aabb.cx(), aabb.cy(), scaledWidth, scaledHeight)

def newUseNode(id_, x, y, href):
    use = Element(addNS('use', 'svg'))
    for name, value in [('id', id_),
                        ('x', str(x)),
                        ('y', str(y)),
                        (addNS('href', 'xlink'), '#' + href)]:
        use.set(name, value)
    return use

def getImageId(bitmapName, width, height):
    return 'image_%s_%.2f_%.2f' % (bitmapName, width, height)

def newImageNode(textureFilename, (w, h), (x, y), textureName):
    image = Element(addNS('image', 'svg'))
    imageAbsURL = getExistingImageFullPath(textureFilename)
    if imageAbsURL is None:
        msg = '%s image file is not present' % textureFilename
        logging.warning(msg)
        return None

    imageFile   = open(imageAbsURL, 'rb').read()
    for name, value in [(addNS('href', 'xlink'),
                         'data:image/%s;base64,%s'
                         % (textureFilename[textureFilename.rfind('.')+1:],
                            base64.encodestring(imageFile))),
                        ('width',  str(w)),
                        ('height', str(h)),
                        ('id',     getImageId(textureName, w, h)),
                        ('x',      str(x)),
                        ('y',      str(y))]:
        image.set(name, value)
    return image

def newGradientNode(id_, stop1, stop2):
    gradientNode = Element(addNS('linearGradient', 'svg'))
    gradientNode.set('id', id_)

    style = 'stop-color:#%s;stop-opacity:%d;'
    for stop in [stop1, stop2]:
        stopNode = Element(addNS('stop', 'svg'))
        for name, value in [('style', style % (stop[0], stop[2])),
                            ('offset', '%d' % stop[1]),
                            ('id', 'stop_%s_%d_%d' % stop)]:
            stopNode.set(name, value)
        gradientNode.append(stopNode)

    return gradientNode

def newRotatedGradientNode(id_, href, angle):
    node = Element(addNS('linearGradient', 'svg'))
    node.set('id', id_)

    gradDirStart = Vector(-1.0, 0.0)
    gradDirEnd = Vector(1.0, 0.0)

    gradDirStart = gradDirStart.rotate(angle)
    gradDirEnd = gradDirEnd.rotate(angle)

    # y is flipped in inkscape
    x1 = (gradDirStart.x * 50.0) + 50.0
    y1 = (gradDirEnd.y * 50.0) + 50.0
    x2 = (gradDirEnd.x * 50.0) + 50.0
    y2 = (gradDirStart.y * 50.0) + 50.0

    for name, value in [('gradientUnits', 'objectBoundingBox'),
                        ('x1', '%d%%' % x1),
                        ('y1', '%d%%' % y1),
                        ('x2', '%d%%' % x2),
                        ('y2', '%d%%' % y2),
                        (addNS('href', 'xlink'), '#%s' % href) ]:
        node.set(name, value)
    return node

def getJointPath(jointType, aabb1, aabb2):
    radius = ENTITY_RADIUS['Joint'] / SVG2LVL_RATIO

    if jointType == 'pivot':
        cx = (aabb1.cx() + aabb2.cx()) / 2.0
        cy = (aabb1.cy() + aabb2.cy()) / 2.0
        return getCenteredCircleSvgPath(cx, cy, radius)
    elif jointType == 'pin':
        w = abs(aabb1.cx() - aabb2.cx())
        h = abs(aabb1.cy() - aabb2.cy())
        if w > h:
            d = 'M %f,%f L %f,%f L %f,%f L %f,%f L %f,%f z' % (
                aabb1.cx(), aabb1.cy()+radius/2.0,
                aabb2.cx(), aabb2.cy()+radius/2.0,
                aabb2.cx(), aabb2.cy()-radius/2.0,
                aabb1.cx(), aabb1.cy()-radius/2.0,
                aabb1.cx(), aabb1.cy()+radius/2.0)
        else:
            d = 'M %f,%f L %f,%f L %f,%f L %f,%f L %f,%f z' % (
                aabb1.cx()-radius/2.0, aabb1.cy(),
                aabb2.cx()-radius/2.0, aabb2.cy(),
                aabb2.cx()+radius/2.0, aabb2.cy(),
                aabb1.cx()+radius/2.0, aabb1.cy(),
                aabb1.cx()-radius/2.0, aabb1.cy())
        return d

# this is the constant which allow to calcultate the bezier curve
# control points
C1 = 0.554

def rectAttrsToPathAttrs(attrs):
    # rect transformation into path:
    #  http://www.w3.org/TR/SVG/shapes.html#RectElement
    #
    # the formulas from svg doesn't work with one rounded corner,
    # so let's try the one from inskcape for that corner (file
    # sp-rect.cpp) inkscape use C (bezier curve) instead of A
    # (elliptic arc)

    #define C1 0.554
    #sp_curve_moveto(c, x + rx, y);
    #if (rx < w2)
    #    sp_curve_lineto(c, x + w - rx, y);
    #sp_curve_curveto(c, x + w - rx * (1 - C1), y,
    #                 x + w, y + ry * (1 - C1),
    #                 x + w, y + ry);
    #if (ry < h2)
    #    sp_curve_lineto(c, x + w, y + h - ry);
    #sp_curve_curveto(c, x + w, y + h - ry * (1 - C1),
    #                 x + w - rx * (1 - C1), y + h,
    #                 x + w - rx, y + h);
    #if (rx < w2)
    #    sp_curve_lineto(c, x + rx, y + h);
    #sp_curve_curveto(c, x + rx * (1 - C1), y + h,
    #                 x, y + h - ry * (1 - C1),
    #                 x, y + h - ry);
    #if (ry < h2)
    #    sp_curve_lineto(c, x, y + ry);
    #sp_curve_curveto(c, x, y + ry * (1 - C1),
    #                 x + rx * (1 - C1), y,
    #                 x + rx, y);

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

    if width == 0.0 or height == 0.0:
        raise Exception('Rectangle %s has its width or its height equals \
        to zero (w=%f, h=%f)' % (attrs['id'], width, height))

    if rx < 0.0 or ry < 0.0:
        raise Exception('Rectangle rx (%f) or ry (%f) is less than zero'
                        % (rx, ry))

    if rx == 0.0:
        rx = ry
    if ry == 0.0:
        ry = rx
    if rx > width / 2.0:
        rx = width / 2.0
    if ry > height / 2.0:
        ry = height / 2.0

    if rx == 0.0 and ry == 0.0:
        d = "M %f,%f " % (x, y)
        d += "L %f,%f " % (x+width, y)
        d += "L %f,%f " % (x+width, y+height)
        d += "L %f,%f " % (x, y+height)
        d += "L %f,%f " % (x, y)
        d += "z"
    else:
        d = "M %f,%f " % (x+rx, y)
        d += "L %f,%f " % (x+width-rx, y)
        d += "C %f,%f %f,%f %f,%f " % (x+width-rx*(1-C1), y,
                                       x+width, y+ry*(1-C1),
                                       x+width, y+ry)
        d += "L %f,%f " % (x+width, y+height-ry)
        d += "A %f,%f %d %d,%d %f,%f " % (rx, ry,
                                          0, 0, 1,
                                          x+width-rx, y+height)
        d += "L %f,%f " % (x+rx, y+height)
        d += "A %f,%f %d %d,%d %f,%f " % (rx, ry, 0, 0, 1, x, y+height-ry)
        d += "L %f,%f " % (x, y+ry)
        d += "A %f,%f %d %d,%d %f,%f " % (rx, ry, 0, 0, 1, x+rx, y)
        d += "z"

    attrs['d'] = d

    return attrs

def getCenteredCircleSvgPath(cx, cy, r):
    path = 'M %f,%f ' % (cx+r, cy)
    path += 'A %f,%f 0 1 1 %f,%f ' % ( r, r, cx-r, cy)
    path += 'A %f,%f 0 1 1 %f,%f' % (r, r, cx+r, cy)
    path += 'z'
    return path
