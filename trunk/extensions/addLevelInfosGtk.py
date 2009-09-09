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

from inksmoto.xmExtGtk import XmExtGtkLevel
from inksmoto.xmotoTools import createIfAbsent, checkId, getValue
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk
TEXTURES = AvailableElements()['TEXTURES']

class AddLevelInfos(XmExtGtkLevel):
    def getWindowInfos(self):
        gladeFile = "addLevelInfos.glade"
        windowName = "addLevelInfos"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {'smooth': ('level', 'smooth', 9, None),
                'lua': ('level', 'lua', '', None),
                'id': ('level', 'id', '', None),
                'name': ('level', 'name', '', None),
                'author': ('level', 'author', '', None),
                'desc': ('level', 'desc', '', None),
                'tex': ('level', 'tex', '_None_', None)}

    def getSignals(self):
        return {'on_tex_clicked': self.updateBitmap}

    def updateLabelData(self):
        if checkId(self.label['level']['id']) == False:
            msg = "The level id can only contains alphanumeric characters and _"
            raise Exception(msg)

        if (len(self.label['level']['id']) == 0
            or len(self.label['level']['name']) == 0):
            raise Exception('You have to set the level id and name')

    def updateBitmap(self, widget):
        imgName = xmGuiGtk.bitmapSelectWindow('Texture Selection',
                                              TEXTURES).run()

        if imgName is not None:
            xmGuiGtk.addImgToBtn(widget, self.get('texLabel'),
                                 imgName, TEXTURES)

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
