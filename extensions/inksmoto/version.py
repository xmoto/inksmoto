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

from .availableElements import AvailableElements
from .xmotoTools import getValue, NOTSET
from os.path import isdir, exists

FUNCTIONS2VERSIONS = AvailableElements()['FUNCTIONS2VERSIONS']
PARAMS2VERSIONS = AvailableElements()['PARAMS2VERSIONS']

class Version:
    def __init__(self):
        # old version... (0.1.1)
        self.x = 0
        self.y = 1
        self.z = 1

    def minVersion(self, options, rootLayer):
        """
        http://wiki.xmoto.tuxfamily.org/index.php?title=Others_tips_to_make_levels
        """
        self.options = options
        if 'sky' in self.options:
            self.addVersion((0, 2, 5))
        if getValue(self.options, 'level', 'tex', default='') != '':
            self.addVersion((0, 2, 5))
        if getValue(self.options, 'level', 'music') not in NOTSET:
            self.addVersion((0, 2, 5))
        if 'remplacement' in self.options:
            for value in list(self.options['remplacement'].values()):
                if value not in NOTSET:
                    self.addVersion((0, 2, 5))
                    break
        if 'layer' in self.options:
            self.addVersion((0, 2, 7))
        
        if getValue(self.options, 'level', 'lua') not in NOTSET:
            self.addVersion((0, 1, 10))
            self.analyseScript(self.options['level']['lua'])

        self.analyseLevelElements(rootLayer)

        return (self.x, self.y, self.z)

    def analyseScript(self, scriptFilename):
        import re

        if isdir(scriptFilename) or not exists(scriptFilename):
            return

        # every word can be a function, we test them all
        function  = re.compile(r'[a-zA-Z0-9]+')
        functions = {}

        f = open(scriptFilename)
        lines = f.readlines()
        f.close()

        for line in lines:
            length = len(line)
            offset = 0
            while True:
                m = function.search(line, offset)
                if m == None:
                    break
                if m:
                    if m.end() >= length:
                        break
                    # we use a dic instead of a set because sets are
                    # available only since python 2.4 (we need 2.3
                    # compatibility for macosx)
                    functions[line[m.start():m.end()]] = ""
                    offset = m.end()

        for function in functions.keys():
            if 'function' in FUNCTIONS2VERSIONS:
                version = FUNCTIONS2VERSIONS[function]
                self.addVersion(version)

    def analyseLevelElements(self, layer):
        if layer.unused == True:
            return

        for child in layer.children:
            self.analyseLevelElements(child)

        for element in layer.elements:
            for namespace, params in element.infos.items():
                if type(params) == dict:
                    for paramKey in params.keys():
                        if (namespace, paramKey) in PARAMS2VERSIONS:
                            version = PARAMS2VERSIONS[(namespace, paramKey)]
                            self.addVersion(version)

    def addVersion(self, version):
        x, y, z = version
        if x > self.x:
            self.x = x
            self.y = y
            self.z = z
        elif x == self.x:
            if y > self.y:
                self.y = y
                self.z = z
            elif y == self.y:
                if z > self.z:
                    self.z = z

