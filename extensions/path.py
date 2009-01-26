from transform import Transform
from factory   import Factory
from inkex     import addNS
import elements
import block_element
import entity_element
import zone_element
import logging, log

class Path:
    def __init__(self, attrs, matrix):
        self.attrs = attrs
        self.matrix = matrix

        if 'transform' in self.attrs:
            self.matrix = self.matrix * Transform().createMatrix(self.attrs['transform'])

    def createElement(self, layerid):
        infos = {}
        style     = {}
        typeid    = 'Block_element'
        id        = self.attrs['id']
        vertex    = self.attrs['d']

        if self.attrs.has_key(addNS('xmoto_label', 'xmoto')):
            dom_label = self.attrs[addNS('xmoto_label', 'xmoto')]
            infos = Factory().createObject('label_parser').parse(dom_label)

            if infos.has_key('typeid'):
                typeid = infos['typeid'] + "_element"

        infos['layerid'] = layerid

        return Factory().createObject(typeid,
                                      id=id, infos=infos, vertex=vertex,
                                      transformMatrix=self.matrix)
