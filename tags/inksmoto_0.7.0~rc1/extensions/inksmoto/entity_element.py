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

from factory import Factory
from elements import Element
from xmotoTools import createIfAbsent, getValue
from availableElements import AvailableElements
from confGenerator import Conf
ENTITY_RADIUS = Conf()['ENTITY_RADIUS']

class Entity(Element):
    def __init__(self, _id, infos, vertex, matrix):
        Element.__init__(self, _id=_id, infos=infos,
                         vertex=vertex, matrix=matrix)
        self.typeid = infos['typeid']
        self.radius = ENTITY_RADIUS[self.typeid]
        self.level = None

    def writeContent(self, options, level):
        """
        - entity:
          * typeid=[PlayerStart|EndOfLevel|Strawberry|Wrecker|ParticleSource|Sprite]
          * size=float_number (the entity colision radius)
          * param_name=param_value
          ** available params are (there's more of them):
             z     (for Sprite)
             name  (for Sprite)
             type  (for ParticleSource)
        """
        self.newWidth = options['width']
        self.newHeight = options['height']
        self.ratio = options['ratio']
        self.level = level

        self.preProcessVertex()
        head = "\t<entity id=\"%s\" typeid=\"%s\">"
        self.content.append(head % (self._id, self.typeid))

        createIfAbsent(self.infos, 'size')

        if 'r' not in self.infos['size']:
            self.infos['size']['r'] = self.radius

        createIfAbsent(self.infos, 'position')

        if ('x' not in self.infos['position']
            or 'y' not in self.infos['position']):
            x, y = self.getEntityPos()
            self.infos['position']['x'] = str(x)
            self.infos['position']['y'] = str(y)

        createIfAbsent(self.level.options, 'remplacement')
        self.calculateNewDimensions()

        self.addElementParams()
        self.content.append("\t</entity>")

        return self.content

    def calculateNewDimensions(self):
        pass

    def getEntityPos(self):
        # use the center of the aabb
        return self.pointInLevelSpace(self.aabb.cx(), self.aabb.cy())

    def calculateNewDimensionsForRemplacement(self, name):
        if name+'Scale' not in self.level.options['remplacement']:
            return

        scale = float(self.level.options['remplacement'][name+'Scale'])
        if scale == 1.0:
            return

        sprite = getValue(self.level.options, 'remplacement',
                          name, default=name)
        self.setSize(sprite, scale)

    def setSize(self, name, scale):
        size = self.infos['size']
        size['r'] = self.radius * scale
        if name in AvailableElements()['SPRITES']:
            sprite = AvailableElements()['SPRITES'][name]
            if 'width' in sprite and 'height' in sprite:
                size['width'] = float(sprite['width']) * scale
                size['height'] = float(sprite['height']) * scale
            else:
                size['width'] = scale
                size['height'] = scale
        else:
            size['width'] = scale
            size['height'] = scale
        
class EndOfLevel(Entity):
    def calculateNewDimensions(self):
        self.calculateNewDimensionsForRemplacement('Flower')

class Strawberry(Entity):
    def calculateNewDimensions(self):
        self.calculateNewDimensionsForRemplacement('Strawberry')

class Sprite(Entity):
    def calculateNewDimensions(self):
        if 'scale' not in self.infos['size']:
            return

        scale = float(self.infos['size']['scale'])
        del self.infos['size']['scale']
        if scale == 1.0:
            return

        if 'param' not in self.infos:
            return
        if 'name' not in self.infos['param']:
            return
        spriteName = self.infos['param']['name']

        self.setSize(spriteName, scale)

class Wrecker(Entity):
    def calculateNewDimensions(self):
        self.calculateNewDimensionsForRemplacement('Wrecker')

def initModule():
    Factory().register('EndOfLevel_element', EndOfLevel)
    Factory().register('Strawberry_element', Strawberry)
    Factory().register('PlayerStart_element', Entity)
    Factory().register('Sprite_element', Sprite)
    Factory().register('Wrecker_element', Wrecker)
    Factory().register('ParticleSource_element', Entity)
    Factory().register('Joint_element', Entity)

initModule()
