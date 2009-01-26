from transform import Transform
from factory   import Factory
from inkex     import addNS
import elements
import block_element
import entity_element
import zone_element
import logging, log

class Path:
    def __init__(self, pathAttributes, matrix):
        self.attributes = pathAttributes
        self.matrix = matrix

        if 'transform' in self.attributes:
            self.matrix = self.matrix * Transform().createMatrix(self.attributes['transform'])

    def createElement(self, layerid):
        infos = {}
        style     = {}
        typeid    = 'Block_element'
        id        = self.attributes['id']
        vertex    = self.attributes['d']

        if self.attributes.has_key(addNS('xmoto_label', 'xmoto')):
            dom_label = self.attributes[addNS('xmoto_label', 'xmoto')]
            infos = Factory().createObject('label_parser').parse(dom_label)

            if infos.has_key('typeid'):
                typeid = infos['typeid'] + "_element"

        infos['layerid'] = layerid

        return Factory().createObject(typeid,
                                      id=id,
                                      input='svg',
                                      infos=infos,
                                      vertex=vertex,
                                      transformMatrix=self.matrix)
