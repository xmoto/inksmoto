from transform import Transform
from factory   import Factory
from aabb import AABB
from lxml import etree
from inkex import addNS
from bezier import Bezier
from parametricArc import ParametricArc
import logging, log

def createNewNode(parentNode, id, tag):
    newNode = etree.SubElement(parentNode, tag)
    if id is not None:
        newNode.set('id', id)
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
    matrix = Transform().createTransformationMatrix(transform)
    matrix = matrix.add_translate(x, y)
    transform = Factory().createObject('transform_parser').unparse(matrix.createTransform())
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
    arcVer = ParametricArc((lastX, lastY), (x, y), (rx,ry),
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
        raise Exception("Can't get AABB of a node which is neither a path nor a rect.\nnode tag:%s" % node.tag)

    return aabb

def getCenteredCircleSvgPath(cx, cy, r):
    return 'M %f,%f A %f,%f 0 1 1 %f,%f A %f,%f 0 1 1 %f,%f z' % (cx+r, cy, r, r, cx-r, cy, r, r, cx+r, cy)

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
    for key, value in node.attrib.iteritems():
        if checkNamespace(node, key) == True:
            del node.attrib[key]

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

    if node.tag == addNS('path', 'svg'):
        node.tag = addNS('rect', 'svg')
        del node.attrib['d']

    node.set('x', str(aabb.x()))
    node.set('y', str(aabb.y()))
    node.set('width', str(aabb.width()))
    node.set('height', str(aabb.height()))
    removeInkscapeAttribute(node)

def addNodeImage(parent, image):
    node = createNewNode(parent, addNS('image', 'svg'))
    node.set(addNS('href', 'xlink'), image)

def getCircleChild(g):
    circle = g.find(addNS('path', 'svg'))
    if circle is None:
        circle = g.find(addNS('rect', 'svg'))
        if circle is None:
            image = g.find(addNS('image', 'svg'))
            if image is None:
                raise Exception('The sprite object is neither a path nor a rect')
            else:
                # the user deleted the circle, lets recreate it
                aabb = getNodeAABB(image)
                id = g.get('id', '')
                pos = id.find('g_')
                if pos != -1:
                    id = id[pos+len('g_'):]
                else:
                    id = None
                circle = createNewNode(g, id, addNS('rect', 'svg'))
                setNodeAsRectangle(circle, aabb)

    return circle