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

import log, logging
from singleton import Singleton

class Factory:
    __metaclass__ = Singleton

    def __init__(self):
        self.objects = {}

    def registerObject(self, name, constructor):
        if name not in self.objects:
            self.objects[name] = constructor
            logging.debug('Factory::%s object added to the factory' % name)

    def createObject(self, name, *args, **keywords):
        if name in self.objects:
            return self.objects[name](*args, **keywords)
        else:
            text = 'Factory::%s object not present in the factory'
            logging.warning(text % name)
            return None
        
