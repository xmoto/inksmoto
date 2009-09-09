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
from parsers import LabelParser
from xmotoTools import getValue, setOrDelBool, setOrDelBitmap
from xmotoTools import delWithoutExcept, updateInfos, setOrDelColor
from xmotoTools import setOrDelValue
from inkex import addNS

class DefaultValues:
    def __init__(self):
        self.defaultValues = {}
        self.svg = None
        self.useDefault = True

    def addElementLabel(self, label):
        """ load default values only for new elements with no xmoto_label
        """
        if len(label.keys()) != 0:
            self.useDefault = False

    def load(self, svg):
        self.svg = svg
        node = self.svg.getMetaDataNode()
        if node is not None:
            label = node.get(addNS('default_xmoto_label', 'xmoto'), '')
            self.defaultValues = LabelParser().parse(label)

    def unload(self, label):
        updateInfos(self.defaultValues, label)

        if len(self.defaultValues.keys()) == 0:
            return

        defaultLabel = LabelParser().unparse(self.defaultValues)
        node = self.svg.getAndCreateMetadataNode()
        node.set(addNS('default_xmoto_label', 'xmoto'), defaultLabel)

    def get(self, dictValues, namespace, name=None, default=None):
        value = getValue(dictValues, namespace, name, None)
        if value is None:
            if self.useDefault == True:
                value = getValue(self.defaultValues, namespace, name, None)
                if value is None:
                    return default
                else:
                    return value
            else:
                return default
        else:
            return value

    def delWithoutExcept(self, _dict, key, namespace=None):
        delWithoutExcept(_dict, key, namespace)
        delWithoutExcept(self.defaultValues, key, namespace)

    def setOrDelBool(self, _dict, namespace, key, value):
        if setOrDelBool(_dict[namespace], key, value) == False:
            delWithoutExcept(self.defaultValues, key, namespace)
            return False
        else:
            return True

    def setOrDelBitmap(self, _dict, namespace, key, bitmapName):
        if setOrDelBitmap(_dict[namespace], key, bitmapName) == False:
            delWithoutExcept(self.defaultValues, key, namespace)

    def setOrDelColor(self, _dict, namespace, prefix, color):
        if setOrDelColor(_dict[namespace], prefix, color) == False:
            delWithoutExcept(self.defaultValues, prefix+'_r', namespace)
            delWithoutExcept(self.defaultValues, prefix+'_g', namespace)
            delWithoutExcept(self.defaultValues, prefix+'_b', namespace)
            delWithoutExcept(self.defaultValues, prefix+'_a', namespace)

    def setOrDelValue(self, _dict, namespace, key, value, default=None):
        if setOrDelValue(_dict[namespace], key, value, default) == False:
            delWithoutExcept(self.defaultValues, key, namespace)
