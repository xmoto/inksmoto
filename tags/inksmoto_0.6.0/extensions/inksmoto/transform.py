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

from singleton import Singleton
from factory   import Factory
from matrix    import Matrix

class Transform:
    __metaclass__ = Singleton

    def __init__(self):
        self.parser = Factory().createObject('transform_parser')

    def createMatrix(self, transforms):
        matrix = Matrix()

        transformElements = self.parser.parse(transforms)

        while len(transformElements) > 0:
            transform = transformElements.pop(0)
            nbParam   = transformElements.pop(0)
            params    = []
            for i in xrange(nbParam):
                params.append(transformElements.pop(0))

            function = getattr(matrix, 'add_'+transform, matrix.error_add)
            matrix = function(*params)

        return matrix
