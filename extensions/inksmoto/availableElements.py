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

from .singleton import Singleton
from .xmotoTools import loadFile

class AvailableElements(metaclass=Singleton):
    def __init__(self):
        self.load()

    def load(self):
        self.vars = {}
        vars = loadFile('listAvailableElements.py')
        for var, value in vars.items():
            self.vars[var.upper()] = value

    def __getitem__(self, var):
        return self.vars[var.upper()]
