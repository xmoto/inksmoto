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

from os.path import join
from os import makedirs
from xmotoTools import getHomeDir, loadFile
from singleton import Singleton

class Conf:
    __metaclass__ = Singleton

    def __init__(self):
        self.read()

    def read(self):
        self.vars = loadFile('xmConf.py')

    def __setitem__(self, var, value):
        self.vars[var] = value

    def __getitem__(self, var):
        return self.vars[var]

    def write(self):
        # xmotoTools.loadFile load in the home directory into the
        # 'inksmoto' dir, so we write the conf file in it.
        userDir = join(getHomeDir(), 'inksmoto')
        if not isdir(userDir):
            makedirs(userDir)
        confFile = join(userDir, 'xmConf.py')
        f = open(confFile, 'wb')
        for key, value in self.vars.iteritems():
            if type(value) == str:
                value = "'%s'" % value
            f.write('%s = %s\n' % (key, value))
        f.close()
