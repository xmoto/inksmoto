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

from inksmoto.xmotoExtensionTkinter import XmExtTkLevel
from inksmoto.xmotoTools import createIfAbsent, checkId, getValue
import Tkinter
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGui
from inksmoto.factory import Factory

class AddLevelInfos(XmExtTkLevel):
    def updateLabelData(self):
        if checkId(self._id.get()) == False:
            msg = "The level id can only contains alphanumeric characters and _"
            raise Exception(msg)

        self.label['level']['smooth'] = self.smooth.get()
        self.label['level']['lua'] = self.lua.get()
        self.label['level']['id'] = self._id.get()
        self.label['level']['name'] = self.name.get()
        self.label['level']['author'] = self.author.get()
        self.label['level']['desc'] = self.desc.get()
        self.label['level']['tex'] = self.tex.get()

        if (len(self.label['level']['id']) == 0
            or len(self.label['level']['name']) == 0):
            raise Exception('You have to set the level id and name')

    def createWindow(self):
        f = Factory()

        createIfAbsent(self.label, 'level')

        xmGui.defineWindowHeader('Level properties')

        value = getValue(self.label, 'level', 'smooth')
        self.smooth = f.createObject('XmScale', 'self.smooth',
                                     value, label='smoothitude :',
                                     from_=1, to=10, resolution=1, default=9)

        value = getValue(self.label, 'level', 'lua')
        self.lua = f.createObject('XmFileSelect', 'self.lua',
                                  value, label='lua script :')

        value = getValue(self.label, 'level', 'id')
        self._id = f.createObject('XmEntry', 'self._id',
                                  value, label='level id :')

        value = getValue(self.label, 'level', 'name')
        self.name = f.createObject('XmEntry', 'self.name',
                                   value, label='level name :')

        value = getValue(self.label, 'level', 'author')
        self.author = f.createObject('XmEntry', 'self.author',
                                     value, label='author :')

        value = getValue(self.label, 'level', 'desc')
        self.desc = f.createObject('XmEntry', 'self.desc',
                                   value, label='description :')

        f.createObject('XmLabel', 'border texture :')
        defaultTexture = getValue(self.label, 'level',
                                  'tex', default='_None_')
        self.tex = f.createObject('XmBitmap', 'self.tex',
                                  AvailableElements()['TEXTURES'][defaultTexture]['file'],
                                  defaultTexture,
                                  toDisplay='textures',
                                  callback=self.updateBitmap,
                                  buttonName='border texture')

    def updateBitmap(self, imgName, buttonName):
        self.tex.update(imgName, AvailableElements()['TEXTURES'])

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
