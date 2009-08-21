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
        self.defDepth = 1.0
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

        self.defaultValues.setOrDelBitmap(self.commonValues, 'usetexture',
                                          'id', self.texture)
        scale = self.scale.get()
        self.defaultValues.setOrDelValue(self.commonValues, 'usetexture',
                                         'scale', scale, self.defScale)

        # block color
        (r, g, b) = self.color.get()
        a = self.color_a.get()
        self.defaultValues.setOrDelColor(self.commonValues, 'usetexture',
                                         'color', (r, g, b, a))
        # handle edges
        createIfAbsent(self.commonValues, 'edge')
        createIfAbsent(self.commonValues, 'edges')

        angle = self.angle.get()
        self.defaultValues.setOrDelValue(self.commonValues, 'edges',
                                         'angle', angle, self.defAngle)

        # edges textures
        self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                          'texture', self.upperEdge)
        self.defaultValues.setOrDelBitmap(self.commonValues, 'edge',
                                          'downtexture', self.downEdge)
        # edges color
        for prefix in ['u', 'd']:
            (r, g, b) = self.__dict__[prefix+'_color'].get()
            a = self.__dict__[prefix+'_a'].get()
            self.defaultValues.setOrDelColor(self.commonValues, 'edge',
                                             prefix, (r, g, b, a))

        # edges scale & depth
        for prefix in ['u', 'd']:
            for (var, default) in [('scale', self.defScale),
                                   ('depth', self.defDepth)]:
                boxName = '_%s_%s_box' % (prefix, var)
                boxWidget = self.__dict__[boxName]
                scaleName = '%s_%s' % (prefix, var)
                if self.defaultValues.setOrDelBool(self.commonValues,
                                                   'edge',
                                                   boxWidget,
                                                   boxName) == True:
                    value = self.__dict__[scaleName].get()
                    self.defaultValues.setOrDelValue(self.commonValues, 'edge',
                                                     scaleName, value, default)
                else:
                    self.defaultValues.delWithoutExcept(scaleName, 'edge')

        # no edge texture selected
        if ('texture' not in self.commonValues['edge']
            and 'downtexture' not in self.commonValues['edge']):
            delWithoutExcept(self.commonValues, 'edge')
            delWithoutExcept(self.commonValues, 'edges')

        return self.commonValues

    def createWindow(self):
        def createColorWidget(prefix, namespace, var, label):
            r = int(self.defaultValues.get(self.commonValues, namespace,
                                           '%s_r' % prefix, default=255))
            g = int(self.defaultValues.get(self.commonValues, namespace,
                                           '%s_g' % prefix, default=255))
            b = int(self.defaultValues.get(self.commonValues, namespace,
                                           '%s_b' % prefix, default=255))
            self.__dict__[var] = f.createObject('XmColor', 'self.%s' % var,
                                                r, g, b, label, grid=(1,1))

        def createEdgeWidgets(prefix, label):
            createColorWidget(prefix, 'edge', prefix+'_color',
                              label+' edge color')

            xmGui.newFrame()
            value = self.defaultValues.get(self.commonValues, 'edge',
                                           prefix+'_a', default=255)
            scale = f.createObject('XmScale',
                                   'self.%s_a' % prefix,
                                   value, label='Alpha',
                                   from_=0, to=255,
                                   resolution=1, default=255)
            self.__dict__[prefix+'_a'] = scale

            xmGui.newFrame()
            value = self.defaultValues.get(self.commonValues, 'edge',
                                           '_%s_scale_box' % prefix)
            box =  f.createObject('XmCheckbox',
                                  'self._%s_scale_box' % prefix,
                                  value, alone=False,
                                  command=lambda: self.boxCallback(prefix+'_scale'))
            self.__dict__['_'+prefix+'_scale_box'] = box
            value = self.defaultValues.get(self.commonValues, 'edge',
                                           prefix+'_scale', default=self.defScale)
            scale = f.createObject('XmScale',
                                   'self.%s_scale' % prefix, value,
                                   label='Scale', from_=0.1, to=10,
                                   resolution=0.1, default=self.defScale)
            self.__dict__[prefix+'_scale'] = scale
            xmGui.popFrame()

            xmGui.newFrame()
            value = self.defaultValues.get(self.commonValues, 'edge',
                                           '_%s_depth_box' % prefix)
            box = f.createObject('XmCheckbox', 'self._%s_depth_box' % prefix,
                                 value, alone=False,
                                 command=lambda: self.boxCallback(prefix+'_depth'))
            self.__dict__['_'+prefix+'_depth_box'] = box
            value = self.defaultValues.get(self.commonValues, 'edge',
                                           prefix+'_depth', default=self.defDepth)
            scale = f.createObject('XmScale',
                                   'self.%s_depth' % prefix, value,
                                   label='Depth', from_=0.1, to=2,
                                   resolution=0.1, default=self.defDepth)
            self.__dict__[prefix+'_depth'] = scale
            xmGui.popFrame()
            xmGui.popFrame(grid=(1, 2))

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

        createColorWidget('color', 'usetexture', 'color', 'Block color')

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
        f.createObject('XmTitle', 'Edge')

        xmGui.newFrame()

        xmGui.newFrame()
        defaultEdge = self.defaultValues.get(self.commonValues, 'edge',
                                             'texture', default='_None_')
        f.createObject('XmLabel', 'Upper edge', grid=(0, 0))
        self.upperEdge = f.createObject('XmBitmap',
                                        'self.upperEdge',
                                        AvailableElements()['EDGETEXTURES'][defaultEdge]['file'],
                                        defaultEdge,
                                        toDisplay='edges',
                                        callback=self.updateBitmap,
                                        grid=(0, 1), buttonName='upperEdge')


        createEdgeWidgets('u', 'Upper')

        xmGui.popFrame()
        xmGui.newFrame()

        defaultDownEdge = self.defaultValues.get(self.commonValues, 'edge',
                                                 'downtexture', default='_None_')
        self.downEdgeLabel = f.createObject('XmLabel',
                                            "Down edge",
                                            grid=(0, 0))
        self.downEdge = f.createObject('XmBitmap',
                                       'self.downEdge',
                                       AvailableElements()['EDGETEXTURES'][defaultDownEdge]['file'],
                                       defaultDownEdge,
                                       toDisplay='edges',
                                       callback=self.updateBitmap,
                                       grid=(0, 1), buttonName='downEdge')

        createEdgeWidgets('d', 'Down')

        xmGui.popFrame()
        xmGui.popFrame()

        label = 'Angle the edges point to (defaulted to 270.0):'
        self.angleLabel = f.createObject('XmLabel', label)
        value = self.defaultValues.get(self.commonValues, 'edges',
                                       'angle', default=self.defAngle)
        self.angle = f.createObject('XmScale',
                                    'self.angle', value,
                                    label='Edge angle', from_=0, to=360,
                                    resolution=5, default=self.defAngle)

        # to update disabled buttons
        for widget in ['u_scale', 'u_depth', 'd_scale', 'd_depth']:
            self.boxCallback(widget)

    def updateBitmap(self, imgName, buttonName):
        if buttonName in ['texture']:
            bitmapDict = AvailableElements()['TEXTURES']
            self.color.resetColor()
        elif buttonName in ['downEdge']:
            bitmapDict = AvailableElements()['EDGETEXTURES']
            self.d_color.resetColor()
        elif buttonName in ['upperEdge']:
            bitmapDict = AvailableElements()['EDGETEXTURES']
            self.u_color.resetColor()

        self.__dict__[buttonName].update(imgName, bitmapDict)

    def boxCallback(self, prefix):
        if self.__dict__['_%s_box' % prefix].get() == 1:
            self.__dict__['%s' % prefix].show()
        else:
            self.__dict__['%s' % prefix].hide()

def run():
    e = ChangeBlockTexture()
    e.affect()
    return e

if __name__ == "__main__":
    run()
