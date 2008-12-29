from transform import Transform
from factory   import Factory
from inkex     import addNS
import elements
import block_element
import entity_element
import zone_element
import logging, log

class Path:
    def __init__(self, pathAttributes, layerTransformMatrix):
        self.attributes      = pathAttributes
        self.transformMatrix = layerTransformMatrix

        if self.attributes.has_key('transform'):
            self.transformMatrix = self.transformMatrix * Transform().createTransformationMatrix(self.attributes['transform'])

    def createElementRepresentedByPath(self, layerid):
        elementInformations = {}
        style     = {}
        typeid    = 'Block_element'
        id        = self.attributes['id']
        vertex    = self.attributes['d']

        if self.attributes.has_key(addNS('xmoto_label', 'xmoto')):
            dom_label = self.attributes[addNS('xmoto_label', 'xmoto')]
            elementInformations = Factory().createObject('label_parser').parse(dom_label)

            if elementInformations.has_key('typeid'):
                typeid = elementInformations['typeid'] + "_element"

        elementInformations['layerid'] = layerid

        return Factory().createObject(typeid,
                                      id=id,
                                      input='svg',
                                      elementInformations=elementInformations,
                                      vertex=vertex,
                                      transformMatrix=self.transformMatrix)
