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
        typeid = 'Block_element'
        id = self.attrs['id']
        vertex = self.attrs['d']

        if addNS('xmoto_label', 'xmoto') in self.attrs:
            dom_label = self.attrs[addNS('xmoto_label', 'xmoto')]
            infos = Factory().createObject('label_parser').parse(dom_label)

            if 'typeid' in infos:
                objectType = infos['typeid'] + "_element"

        infos['layerid'] = layerid

        return Factory().createObject(objectType,
                                      id=id, infos=infos, vertex=vertex,
                                      transformMatrix=self.matrix)
