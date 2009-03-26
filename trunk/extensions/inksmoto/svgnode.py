import base64
from transform import Transform
from factory   import Factory
from aabb import AABB
from lxml import etree
from inkex import addNS
from bezier import Bezier
from parametricArc import ParametricArc
from xmotoTools import getExistingImageFullPath, getValue
from lxml.etree import Element
from availableElements import AvailableElements
from matrix import Matrix
from vector import Vector
import logging
from confGenerator import Conf
ENTITY_RADIUS = Conf()['ENTITY_RADIUS']
SVG2LVL_RATIO = Conf()['SVG2LVL_RATIO']

def createNewNode(parentNode, _id, tag):
    newNode = etree.SubElement(parentNode, tag)
    if _id is not None:
        newNode.set('id', _id)
    return newNode

def duplicateNode(node, newId):
    parentNode = node.getparent()
    newNode = createNewNode(parentNode, newId, node.tag)
    for key, value in node.items():
        if checkNamespace(node, key) == False:
            newNode.set(key, value)
    newNode.set('id', newId)
    return newNode

def newParent(node, new):
    # to set a new parent for a node, there's no need to remove it
    # from it's old parent
    new.append(node)

def translateNode(node, x, y):
    transform = node.get('transform', default='')
    matrix = Transform().createMatrix(transform)
    matrix = matrix.add_translate(x, y)
    parser = Factory().createObject('transform_parser')
    transform = parser.unparse(matrix.createTransform())
    node.set('transform', transform)

def addBezierToAABB(aabb, (lastX, lastY), params):
    x1, y1 = params['x1'], params['y1']
    x2, y2 = params['x2'], params['y2']
    x,  y  = params['x'],  params['y']
    bezVer = Bezier(((lastX, lastY), (x1, y1), (x2, y2), (x, y))).splitCurve()
    for cmd, values in bezVer:
        aabb.addPoint(values['x'], values['y'])

def addArcToAABB(aabb, (lastX, lastY), params):
    x,  y  = params['x'],  params['y']
    rx, ry = params['rx'], params['ry']
    arcVer = ParametricArc((lastX, lastY), (x, y), (rx, ry),
                           params['x_axis_rotation'], 
                           params['large_arc_flag'], 
                           params['sweep_flag']).splitArc()
    for cmd, values in arcVer:
        aabb.addPoint(values['x'], values['y'])

def getNodeAABB(node):
    aabb = AABB()

    lastX = 0
    lastY = 0

    if node.tag == addNS('path', 'svg'):
        vertex = Factory().createObject('path_parser').parse(node.get('d'))
        if vertex is None:
            raise Exception("Node %s has no attribute d" % str(node))
        for (cmd, values) in vertex:
            if values is not None:
                if cmd == 'C':
                    addBezierToAABB(aabb, (lastX, lastY), values)
                elif cmd == 'A':
                    addArcToAABB(aabb, (lastX, lastY), values)
                else:
                    aabb.addPoint(values['x'], values['y'])

                lastX = values['x']
                lastY = values['y']

    elif node.tag in [addNS('rect', 'svg'), addNS('image', 'svg')]:
        x = float(node.get('x'))
        y = float(node.get('y'))
        width  = float(node.get('width'))
        height = float(node.get('height'))
        aabb.addPoint(x, y)
        aabb.addPoint(x + width, y + height)

    else:
        raise Exception("Can't get AABB of a node which is neither a path \
nor a rect.\nnode tag:%s" % node.tag)

    return aabb

def getCenteredCircleSvgPath(cx, cy, r):
    path = 'M %f,%f ' % (cx+r, cy)
    path += 'A %f,%f 0 1 1 %f,%f ' % ( r, r, cx-r, cy)
    path += 'A %f,%f 0 1 1 %f,%f' % (r, r, cx+r, cy)
    path += 'z'
    return path

def getParsedLabel(node):
    label = node.get(addNS('xmoto_label', 'xmoto'), '')
    parser = Factory().createObject('label_parser')
    return parser.parse(label)

def checkNamespace(node, attrib):
    pos1 = attrib.find('{')
    pos2 = attrib.find('}')
    if pos1 != -1 and pos2 != -1:
        namespace = attrib[pos1+1:pos2]
        if namespace in [node.nsmap['inkscape'], node.nsmap['sodipodi']]:
            return True
    return False

def removeInkscapeAttribute(node):
    # if you only change the 'd' attribute the shape won't be
    # update in inkscape as inkscape uses it's own attributes
    for key in node.attrib.keys():
        if checkNamespace(node, key) == True:
            del node.attrib[key]

def subLayerElementToSingleNode(node):
    aabb = None
    if isSubLayerElement(node) == True:
        aabb = getNodeAABB(getCircleChild(node))
        deleteChildren(node)
        id_ = node.get('id', '')
        pos = id_.find('g_')
        if pos != -1:
            id_ = id_[pos+2:]
            node.set('id', id_)

    return aabb

def isSubLayerElement(node):
    """ a sub-layer element has an xmoto_label
    """
    if node.tag == addNS('g', 'svg'):
        return node.get(addNS('xmoto_label', 'xmoto'), '') != ''
    else:
        return False

def deleteChildren(node):
    for child in node.getchildren():
        node.remove(child)

def setNodeAsCircle(node, r, aabb=None):
    if aabb is None:
        aabb = getNodeAABB(node)

    if node.tag == addNS('rect', 'svg'):
        node.tag = addNS('path', 'svg')

    node.set('d', getCenteredCircleSvgPath(aabb.cx(), aabb.cy(), r))
    removeInkscapeAttribute(node)

def setNodeAsRectangle(node, aabb=None):
    if aabb is None:
        aabb = getNodeAABB(node)

    if node.tag != addNS('rect', 'svg'):
        node.tag = addNS('rect', 'svg')
        if 'd' in node.attrib:
            del node.attrib['d']

    node.set('x', str(aabb.x()))
    node.set('y', str(aabb.y()))
    node.set('width', str(aabb.width()))
    node.set('height', str(aabb.height()))
    removeInkscapeAttribute(node)

def getImageNodes(node):
    if node.tag != addNS('g', 'svg'):
        # the user selected the circle or the image instead of the
        # sublayer or the object is not a bitmap yet
        parent = node.getparent()
        if (parent.tag == addNS('g', 'svg')
            and parent.get(addNS('xmoto_label', 'xmoto')) is not None):
            g = parent
        else:
            g = createNewNode(parent,
                              'g_' + node.get('id', ''),
                              addNS('g', 'svg'))
            newParent(node, g)
    else:
        g = node

    try:
        circle = getCircleChild(g)
    except Exception, e:
        _id = g.get('id', '')
        logging.warning("Sprite [%s] is an empty layer\n%s" % (_id, e))
        return (g, None, None)

    use = g.find(addNS('use', 'svg'))
    if use is None:
        # deprecated, we no longer use images, uses instead
        image  = g.find(addNS('image', 'svg'))
        if image is not None:
            g.remove(image)

    return (g, circle, use)

def setNodeAsBitmap(node, svg, texName, radius, bitmaps, label, style,
                    scale=1.0, _reversed=False, rotation=0.0):

    (g, circle, use) = getImageNodes(node)

    # set the xmoto_label on both the sublayer and the
    # circle (for backward compatibility)
    g.set(addNS('xmoto_label', 'xmoto'), label)

    circle.set(addNS('xmoto_label', 'xmoto'), label)
    circle.set('style', style)

    if g.get('style') is not None:
        del g.attrib['style']

    setNodeAsCircle(circle, scale * radius)

    # set the circle transform to the layer
    transform = circle.get('transform')
    if transform is not None:
        g.set('transform', transform)
        del circle.attrib['transform']

    (x, y, cx, cy, width, height) = getImageDimensions(texName, scale, circle)

    imageId = svg.addImage(texName, bitmaps, width, height)

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
        transformNode(use, rotation, _reversed, (cx, cy))

        # set the label on the image to check after a change
        # if the image need some change too
        use.set(addNS('saved_xmoto_label', 'xmoto'), label)

def getImageDimensions(texName, scale, node):
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

    aabb = getNodeAABB(node)
    x = aabb.cx() - cx
    # with the same coordinates, inkscape doesn't display
    # images at the same place as xmoto ...
    y = aabb.cy() - scaledHeight + cy

    return (x, y, aabb.cx(), aabb.cy(), scaledWidth, scaledHeight)

def transformNode(node, rotation, reversed_, (tx, ty)):
    matrix = Matrix()
    if 'transform' in node.attrib:
        del node.attrib['transform']

    # translate around the origin, do the transfroms
    # then translate back.
    matrix = matrix.add_translate(tx, ty)

    if rotation != 0.0:
        matrix = matrix.add_rotate(-rotation)
    if reversed_ == True:
        matrix = matrix.add_scale(-1, 1)

    matrix = matrix.add_translate(-tx, -ty)

    if matrix != Matrix():
        parser = Factory().createObject('transform_parser')
        transform = parser.unparse(matrix.createTransform())
        node.set('transform', transform)

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

    x1 = (gradDirStart.x() * 50.0) + 50.0
    x2 = (gradDirEnd.x() * 50.0) + 50.0
    y1 = (gradDirEnd.y() * 50.0) + 50.0
    y2 = (gradDirStart.y() * 50.0) + 50.0

    for name, value in [('gradientUnits', 'objectBoundingBox'),
                        ('x1', '%d%%' % x1),
                        ('y1', '%d%%' % y1),
                        ('x2', '%d%%' % x2),
                        ('y2', '%d%%' % y2),
                        (addNS('href', 'xlink'), '#%s' % href) ]:
        node.set(name, value)
    return node

def getCircleChild(g):
    circle = g.find(addNS('path', 'svg'))
    if circle is None:
        circle = g.find(addNS('rect', 'svg'))
        if circle is None:
            image = g.find(addNS('image', 'svg'))
            if image is None:
                raise Exception('The sprite object is neither a path, \
a rect nor an image')
            else:
                # the user deleted the circle, lets recreate it
                aabb = getNodeAABB(image)
                _id = g.get('id', '')
                pos = _id.find('g_')
                if pos != -1:
                    _id = _id[pos+len('g_'):]
                else:
                    _id = None
                circle = createNewNode(g, _id, addNS('rect', 'svg'))
                setNodeAsRectangle(circle, aabb)

    return circle

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

    if width == 0 or height == 0:
        raise Exception('Rectangle %s has its width or its height equals \
        to zero' % attrs['id'])

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
