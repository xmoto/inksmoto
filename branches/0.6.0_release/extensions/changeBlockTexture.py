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

from inksmoto.xmotoExtensionTkinter import XmExtTkElement
from inksmoto.xmotoTools import createIfAbsent, delWithoutExcept, NOTSET_BITMAP
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGui
from inksmoto.factory import Factory

class ChangeBlockTexture(XmExtTkElement):
    def __init__(self):
        XmExtTkElement.__init__(self)
        self.defScale = 1.0
        self.defAngle = 270.0
        self.defMethod = 'angle'
        self.namespacesInCommon = ['usetexture', 'edge', 'edges']

    def getUserChanges(self):
        delWithoutExcept(self.commonValues, 'usetexture')
        delWithoutExcept(self.commonValues, 'edge')
        delWithoutExcept(self.commonValues, 'edges')
        # if the block has been set as an entity
        delWithoutExcept(self.commonValues, 'typeid')

        # handle texture
        createIfAbsent(self.commonValues, 'usetexture')

        if self.texture.get() in NOTSET_BITMAP:
            raise Exception('You have to give a texture to the block')

        self.defaultValues.setOrDelBitmap(self.commonValues, 'usetexture', 'id', self.texture)
        scale = self.scale.get()
        if scale != self.defScale:
            self.commonValues['usetexture']['scale'] = scale

        # block color
        (r, g, b) = self.color.get()
        a = self.color_a.get()
        default = 255
        if ( r != default or g != default or b != default or a != default):
            self.commonValues['usetexture']['color_r'] = r
            self.commonValues['usetexture']['color_g'] = g
            self.commonValues['usetexture']['color_b'] = b
            self.commonValues['usetexture']['color_a'] = a
        else:
            delWithoutExcept(self.commonValues['usetexture'], 'color_r')
            delWithoutExcept(self.commonValues['usetexture'], 'color_g')
            delWithoutExcept(self.commonValues['usetexture'], 'color_b')
            delWithoutExcept(self.commonValues['usetexture'], 'color_a')

        # handle edges
        createIfAbsent(self.commonValues, 'edge')
        createIfAbsent(self.commonValues, 'edges')

        drawMethod = self.drawMethod.get()
        if drawMethod != self.defMethod:
            self.commonValues['edges']['drawmethod'] = drawMethod
        if drawMethod in ['angle']:
            angle = self.angle.get()
            if angle != self.defAngle:
                self.commonValues['edges']['angle'] = angle

            self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                              'texture', self.upperEdge)
            self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                              'downtexture', self.downEdge)

            # no edge texture selected
            if ('texture' not in self.commonValues['edge']
                and 'downtexture' not in self.commonValues['edge']):
                delWithoutExcept(self.commonValues, 'edge')
                delWithoutExcept(self.commonValues, 'edges')

        elif drawMethod in ['in', 'out']:
            delWithoutExcept(self.commonValues['edges'], 'angle')
            delWithoutExcept(self.commonValues['edge'],  'downtexture')
            self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                              'texture', self.upperEdge)

            # no edge texture selected
            if 'texture' not in self.commonValues['edge']:
                delWithoutExcept(self.commonValues, 'edge')
                delWithoutExcept(self.commonValues, 'edges')

        return self.commonValues

    def createWindow(self):
        f = Factory()
        xmGui.defineWindowHeader(title='Block textures')

        # texture
        f.createObject('XmTitle', "Texture")
        f.createObject('XmLabel', "Click the texture to choose another one.")

        xmGui.newFrame()
        xmGui.newFrame()

        defaultTexture = self.defaultValues.get(self.commonValues, 'usetexture',
                                                'id', default='_None_')
        self.texture = f.createObject('XmBitmap',
                                      'self.texture',
                                      AvailableElements()['TEXTURES'][defaultTexture]['file'],
                                      defaultTexture,
                                      toDisplay='textures',
                                      callback=self.updateBitmap,
                                      grid=(0, 1),
                                      buttonName='texture')

        r = int(self.defaultValues.get(self.commonValues, 'usetexture',
                                       'color_r', default=255))
        g = int(self.defaultValues.get(self.commonValues, 'usetexture',
                                       'color_g', default=255))
        b = int(self.defaultValues.get(self.commonValues, 'usetexture',
                                       'color_b', default=255))
        self.color = f.createObject('XmColor', 'self.color', r, g, b,
                                    'Block color', grid=(1,1))

        xmGui.popFrame()

        value = self.defaultValues.get(self.commonValues, 'usetexture', 'scale',
                                       default=self.defScale)
        self.scale = f.createObject('XmScale',
                                    'self.scale', value, alone=False,
                                    label='Scale', from_=0.1, to=10,
                                    resolution=0.1, default=self.defScale)

        value = self.defaultValues.get(self.commonValues, 'usetexture', 'color_a')
        self.color_a = f.createObject('XmScale', 'self.color_a', value, alone=False,
                                      label='alpha color:', from_=0, to=255,
                                      resolution=1, default=255)

        xmGui.popFrame()

        # edges
        f.createObject('XmTitle', "Edge")
        f.createObject('XmLabel', "Edge drawing behaviour:")
        buttons = [('using the given angle', 'angle'),
                   ('inside the block', 'in'),
                   ('outside the block', 'out')]
        value = self.defaultValues.get(self.commonValues, 'edges',
                                       'drawmethod', default='angle')
        self.drawMethod = f.createObject('XmRadio', 'self.drawMethod', value,
                                         buttons, command=self.edgeDrawCallback)

        xmGui.newFrame()
        defaultEdge = self.defaultValues.get(self.commonValues, 'edge',
                                             'texture', default='_None_')
        f.createObject('XmLabel', "Upper edge texture", grid=(0, 0))
        self.upperEdge = f.createObject('XmBitmap',
                                        'self.upperEdge',
                                        AvailableElements()['EDGETEXTURES'][defaultEdge]['file'],
                                        defaultEdge,
                                        toDisplay='edges',
                                        callback=self.updateBitmap,
                                        grid=(0, 1), buttonName='upperEdge')

        defaultDownEdge = self.defaultValues.get(self.commonValues, 'edge',
                                                 'downtexture', default='_None_')
        self.downEdgeLabel = f.createObject('XmLabel',
                                            "Down edge texture",
                                            grid=(1, 0))
        self.downEdge = f.createObject('XmBitmap',
                                       'self.downEdge',
                                       AvailableElements()['EDGETEXTURES'][defaultDownEdge]['file'],
                                       defaultDownEdge,
                                       toDisplay='edges',
                                       callback=self.updateBitmap,
                                       grid=(1, 1), buttonName='downEdge')
        xmGui.popFrame()

        label = "Angle the edges point to (defaulted to 270.0):"
        self.angleLabel = f.createObject('XmLabel', label)
        value = self.defaultValues.get(self.commonValues, 'edges',
                                       'angle', default=self.defAngle)
        self.angle = f.createObject('XmScale',
                                    'self.angle', value,
                                    label='Edge angle', from_=0, to=360,
                                    resolution=45, default=self.defAngle)

        # to update disabled buttons
        self.edgeDrawCallback()

    def edgeDrawCallback(self):
        method = self.drawMethod.get()
        if method in ['angle']:
            self.angle.show()
            self.downEdgeLabel.show()
            self.downEdge.show()
        elif method in ['in', 'out']:
            self.angle.hide()
            self.downEdgeLabel.hide()
            self.downEdge.hide()

    def updateBitmap(self, imgName, buttonName):
        if buttonName in ['texture']:
            bitmapDict = AvailableElements()['TEXTURES']
        elif buttonName in ['downEdge', 'upperEdge']:
            bitmapDict = AvailableElements()['EDGETEXTURES']

        self.__dict__[buttonName].update(imgName, bitmapDict)

def run():
    e = ChangeBlockTexture()
    e.affect()
    return e

if __name__ == "__main__":
    run()
