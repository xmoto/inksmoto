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

from .parsers import LabelParser, StyleParser
from .factory import Factory

class xmIn:
    def __init__(self, node):
        self.node = node

    def getLabel(self):
        pass

class xmOut:
    def __init__(self, node):
        self.node = node

    def update(self, label):
        pass


class xmObject(type):
    def __init__(self, in_, out):
        self.in_ = in_
        self.out = out

class xmEntity(xmObject):
    pass

class xmPlayerStart(xmEntity):
    pass

class xmEndOfLevel(xmEntity):
    pass

class xmParticleSource(xmEntity):
    pass

class xmSprite(xmEntity):
    pass

class xmStrawberry(xmEntity):
    def __init__(self, ):
        xmEntity.__init__(self, )

class xmWrecker(xmEntity):
    pass

class xmZone(xmEntity):
    pass

class xmJoint(xmEntity):
    pass

class xmBlock(xmObject):
    pass


class xmObjectsFactory(Factory):
    def __init__(self):
        pass

    def createFromXmIn(self, in_, out):
        """ 
            -no xm_label on the node: xmNone
            -xm_label but no typeid in it: xmBlock
            -xm_label and typeid: xmEntity
        """
        label = in_.getLabel()

        if label != {} and 'typeid' in label:
            name = label['typeid']
        else:
            name = 'Block'

        if name in self.objects:
            return self.objects[name](in_, out)
        else:
            raise Exception("Object %s not registered in the factory" % name)

def initModule():
    xmObjectsFactory().register('PlayerStart', xmPlayerStart)
    xmObjectsFactory().register('EndOfLevel', xmEndOfLevel)
    xmObjectsFactory().register('ParticleSource', xmParticleSource)
    xmObjectsFactory().register('Sprite', xmSprite)
    xmObjectsFactory().register('Strawberry', xmStrawberry)
    xmObjectsFactory().register('Wrecker', xmWrecker)
    xmObjectsFactory().register('Zone', xmZone)
    xmObjectsFactory().register('Joint', xmJoint)
    xmObjectsFactory().register('Block', xmBlock)

initModule()
