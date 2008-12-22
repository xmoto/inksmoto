from transform import Transform
from factory   import Factory
from aabb import AABB
from lxml import etree
from inkex import addNS
from xmotoTools import checkNamespace
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
