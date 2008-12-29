from transform import Transform
from factory   import Factory
from aabb import AABB
from lxml import etree
from inkex import addNS
import logging, log

def duplicateNode(node, newId):
    newNode = etree.Element(node.tag)
    node.xpath('..')[0].append(newNode)
    for key, value in node.items():
        if checkNamespace(node, key) == False:
            newNode.set(key, value)
    newNode.set('id', newId)
    return newNode

def translateNode(node, x, y):
    transform = node.get('transform', default='')
    matrix = Transform().createTransformationMatrix(transform)
    matrix = matrix.add_translate(x, y)
    transform = Factory().createObject('transform_parser').unparse(matrix.createTransform())
    node.set('transform', transform)

def getNodeAABB(node):
    aabb = AABB()

    if node.tag == addNS('path', 'svg'):
        vertex = Factory().createObject('path_parser').parse(node.get('d'))
        if vertex is None:
            raise Exception("Node %s has no attribute d" % str(node))
        for (cmd, values) in vertex:
            if values is not None:
                aabb.addPoint(values['x'], values['y'])

    elif node.tag == addNS('rect', 'svg'):
        x = float(node.get('x'))
        y = float(node.get('y'))
        width  = float(node.get('width'))
        height = float(node.get('height'))
        aabb.addPoint(x, y)
        aabb.addPoint(x + width, y + height)

    else:
        raise Exception("Can't get AABB of a node which is neither a path nor a rect.\nnode tag:%s" % node.tag)

    return aabb

def getCircleSvgPath(x, y, r):
    return 'M %f,%f A %f,%f 0 1 1 %f,%f A %f,%f 0 1 1 %f,%f z' % (x, y, r, r, x-2*r, y, r, r, x, y)

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

def setNodeAsCircle(node, r):
    aabb = getNodeAABB(node)

    if node.tag == addNS('rect', 'svg'):
        node.tag = addNS('path', 'svg')

    node.set('d', getCenteredCircleSvgPath(aabb.cx(), aabb.cy(), r))
    removeInkscapeAttribute(node)
