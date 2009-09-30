#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

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
            infos = Factory().create('label_parser').parse(dom_label)

            if 'typeid' in infos:
                objectType = infos['typeid'] + "_element"

        infos['layerid'] = layerid

        return Factory().create(objectType, _id=_id, infos=infos, vertex=vertex,
                                matrix=self.matrix)
