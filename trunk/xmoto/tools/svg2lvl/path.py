from transform import Transform
from factory   import Factory
import elements
import logging, log

class Path:
    def __init__(self, pathAttributes, layerTransformMatrix):
        self.attributes      = pathAttributes
        self.transformMatrix = layerTransformMatrix

        if self.attributes.has_key('transform'):
            self.transformMatrix = self.transformMatrix * Transform().createTransformationMatrix(self.attributes['transform'])

    def createElementRepresentedByPath(self):
        elementInformations = {}
        typeid    = 'Block_element'
        id        = self.attributes['id']
        vertex    = self.attributes['d']

        if self.attributes.has_key('inkscape:label'):
            dom_label = self.attributes['inkscape:label']
            elementInformations = Factory().createObject('label_parser').parse(dom_label)

            if elementInformations.has_key('typeid'):
                typeid = elementInformations['typeid'] + "_element"

        return Factory().createObject(typeid,
                                      id,
                                      elementInformations,
                                      vertex,
                                      self.transformMatrix)
