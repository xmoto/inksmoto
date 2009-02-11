from transform import Transform
from factory import Factory
from inkex import addNS

class Path:
    def __init__(self, attrs, matrix):
        self.attrs = attrs
        self.matrix = matrix

        if 'transform' in self.attrs:
            self.matrix *= Transform().createMatrix(self.attrs['transform'])

    def createElement(self, layerid):
        infos = {}
        _id = self.attrs['id']
        vertex = self.attrs['d']
        objectType = 'Block_element'

        if addNS('xmoto_label', 'xmoto') in self.attrs:
            dom_label = self.attrs[addNS('xmoto_label', 'xmoto')]
            infos = Factory().createObject('label_parser').parse(dom_label)

            if 'typeid' in infos:
                objectType = infos['typeid'] + "_element"

        infos['layerid'] = layerid

        return Factory().createObject(objectType,
                                      _id=_id, infos=infos, vertex=vertex,
                                      matrix=self.matrix)
