#!/bin/python
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
from xmotoExtension import XmExt
from defaultValues import DefaultValues
from xmotoTools import createIfAbsent, applyOnElements, delWithoutExcept
from xmotoTools import getExistingImageFullPath, conv8to16, conv16to8, getValue
from xmotoTools import setOrDelBool, setOrDelValue, setOrDelColor
from xmotoTools import setOrDelBitmap
from inkex import addNS
from parsers import LabelParser
import xmGuiGtk
from inksmoto.availableElements import AvailableElements

class XmExtGtk(XmExt):
    def createWindow(self, okFunc):
        (gladeFile, windowName) = self.getWindowInfos()
        self.wTree = xmGuiGtk.createWindow(gladeFile, windowName)
        window = self.get(windowName)
        window.connect("destroy", xmGuiGtk.quit)

        _dic = {"on_apply_clicked" : okFunc,
                "on_cancel_clicked" : xmGuiGtk.quit}
        self.wTree.signal_autoconnect(_dic)

        signals = self.getSignals()
        if signals is not None:
            self.registerSignals(signals)

    def mainLoop(self):
        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
        else:
            xmGuiGtk.mainLoop()

    def get(self, widgetName):
        return self.wTree.get_widget(widgetName)

    def registerSignals(self, signals):
        for signal, func in signals.iteritems():
            self.wTree.signal_connect(signal, func)

    def fillWindowValues(self, values):
        """ get a dict with 'widgetName': (ns, key, default,
            accessors). For each widget in the dict, get the value
            from the svg and set it to the widget
        """
        import gtk

        for widgetName, (ns, key, default, accessors) in values.iteritems():
            value = self.getValue(ns, key, default)
            widget = self.get(widgetName)
            if widget.__class__ == gtk.CheckButton:
                # CheckButton
                if value == 'true':
                    value = True
                else:
                    value = False
                widget.set_active(value)
            elif widget.__class__ == gtk.HScale:
                # HScale
                if accessors is not None:
                    (setter, getter) = accessors
                    value = setter(float(value))
                else:
                    value = float(value)
                widget.set_value(value)
            elif widget.__class__ == gtk.Button:
                # Button
                label = self.get(widgetName+'Label')
                if label is not None:
                    # if a label is present, it's a bitmapped button
                    imgName = value
                    img = None
                    bitmapDict = None
                    for type in ['TEXTURES', 'EDGETEXTURES',
                                 'PARTICLESOURCES', 'SPRITES']:
                        try:
                            bitmapDict = AvailableElements()[type]
                            img = bitmapDict[value]['file']
                        except:
                            pass
                        else:
                            break
                    if img is not None:
                        xmGuiGtk.addImgToBtn(widget, label, imgName, bitmapDict)
            elif widget.__class__ == gtk.ColorButton:
                # ColorButton
                r = self.getValue(ns, key+'_r', default)
                g = self.getValue(ns, key+'_g', default)
                b = self.getValue(ns, key+'_b', default)
                a = self.getValue(ns, key+'_a', default)
                widget.set_color(gtk.gdk.Color(conv8to16(int(r)),
                                               conv8to16(int(g)),
                                               conv8to16(int(b))))
                widget.set_alpha(conv8to16(int(a)))
            elif widget.__class__ == gtk.Entry:
                widget.set_text(value)
            elif widget.__class__ == gtk.FileChooserButton:
                widget.set_filename(value)

    def fillResults(self, dict_):
        import gtk

        if self.widgetsInfos is None:
            return

        self.fillResultsPreHook()
        
        for widgetName in self.widgetsInfos.keys():
            widget = self.wTree.get_widget(widgetName)
            (ns, key, default, accessors) = self.widgetsInfos[widgetName]
            createIfAbsent(dict_, ns)

            if widget.__class__ == gtk.CheckButton:
                bool = widget.get_active()
                self.setOrDelBool(ns, key, bool)
            elif widget.__class__ == gtk.HScale:
                value = widget.get_value()
                if accessors is not None:
                    (setter, getter) = accessors
                    value = getter(value)
                self.setOrDelValue(ns, key, value, default)
            elif widget.__class__ == gtk.Button:
                label = self.get(widgetName+'Label')
                if label is not None:
                    bitmap = label.get_text()
                    self.setOrDelBitmap(ns, key, bitmap)
            elif widget.__class__ == gtk.ColorButton:
                color = widget.get_color()
                (r, g, b) = (conv16to8(color.red),
                             conv16to8(color.green),
                             conv16to8(color.blue))
                a = conv16to8(widget.get_alpha())
                self.setOrDelColor(ns, key, (r, g, b, a))
            elif widget.__class__ == gtk.Entry:
                text = widget.get_text()
                self.setOrDelValue(ns, key, text, default)
            elif widget.__class__ == gtk.FileChooserButton:
                fileName = widget.get_filename()
                self.setOrDelValue(ns, key, fileName, default)

        self.removeUnusedNs(dict_)

    def removeUnusedNs(self, dict_):
        toDel = []
        for ns in dict_.iterkeys():
            if dict_[ns] == {}:
                toDel.append(ns)
        for ns in toDel:
            del dict_[ns]

    # the methods to implement in final extensions
    def getWindowInfos(self):
        return None

    def getSignals(self):
        return None

    # the methods to implement in direct children
    def fillResultsPreHook(self):
        pass

    def getValue(self, ns, key, default):
        return None

    def setOrDelBool(self, ns, key, value):
        pass

    def setOrDelValue(self, ns, key, value, default):
        pass

    def setOrDelBitmap(self, ns, key, value):
        pass

    def setOrDelColor(self, ns, key, value):
        pass

class XmExtGtkLevel(XmExtGtk):
    """ update level's properties
    """
    def load(self):
        (self.node, metadata) = self.svg.getMetaData()
        self.label = LabelParser().parse(metadata)

    def store(self, widget):
        try:
            self.fillResults(self.label)
            self.updateLabelData()
        except Exception, e:
            logging.error(str(e))
            xmGuiGtk.errorMessageBox(str(e))
            xmGuiGtk.quit()
            return

        metadata = LabelParser().unparse(self.label)

        if self.node is not None:
            self.node.text = metadata
        else:
            self.svg.createMetadata(metadata)

        xmGuiGtk.quit()

    def effect(self):
        self.svg.setDoc(self.document)
        self.load()
        self.createWindow(self.store)

        self.widgetsInfos = self.getWidgetsInfos()
        if self.widgetsInfos is not None:
            self.fillWindowValues(self.widgetsInfos)

        self.mainLoop()
        self.afterHook()

    def getValue(self, ns, key, default):
        return getValue(self.label, ns, key, default)

    def setOrDelBool(self, ns, key, bool):
        setOrDelBool(self.label[ns], key, bool)

    def setOrDelValue(self, ns, key, value, default):
        setOrDelValue(self.label[ns], key, value, default)

    def setOrDelBitmap(self, ns, key, bitmap):
        setOrDelBitmap(self.label[ns], key, bitmap)

    def setOrDelColor(self, ns, key, color):
        setOrDelColor(self.label[ns], key, color)

    # the methods to implements in child
    def updateLabelData(self):
        pass

    def afterHook(self):
        pass


class XmExtGtkElement(XmExtGtk):
    """ update elements' properties
    """
    def __init__(self):
        XmExtGtk.__init__(self)
        # the dictionnary which contains the elements informations
        self.comVals = {}
        self.namespacesInCommon = None
        self.namespacesToDelete = []
        self.originalValues = {}
        self.defVals = DefaultValues()

    def okPressed(self, widget=None):
        if self.effectUnloadHook() == True:
            try:
                self.fillResults(self.comVals)
                self.label = self.getUserChanges()
            except Exception, e:
                logging.error(str(e))
                xmGuiGtk.errorMessageBox(str(e))
                xmGuiGtk.quit()
                return

            applyOnElements(self, self.selected, self.updateContent)
            self.defVals.unload(self.label)

        xmGuiGtk.quit()

    def effect(self):
        """ load the selected objects, create the window and set the
            widgets values.
        """
        if len(self.selected) == 0:
            return

        self.svg.setDoc(self.document)

        (_quit, applyNext) = self.effectLoadHook()
        if _quit == True:
            return
        if applyNext == True:
            self.defVals.load(self.svg)
            applyOnElements(self, self.selected, self.addPath)

        self.createWindow(self.okPressed)

        self.widgetsInfos = self.getWidgetsInfos()
        if self.widgetsInfos is not None:
            self.fillWindowValues(self.widgetsInfos)

        self.mainLoop()

    def addPath(self, path):
        # put None if a value is different in at least two path
        label = path.get(addNS('xmoto_label', 'xmoto'), '')
        label = LabelParser().parse(label)

        self.defVals.addElementLabel(label)

        elementId = path.get('id', '')
        for name, value in label.iteritems():
            if type(value) == dict:
                namespace    = name
                namespaceDic = value

                # save original xmotoLabel to put back parameters not
                # modified by this extension
                if (self.namespacesInCommon is not None
                    and namespace not in self.namespacesInCommon):
                    createIfAbsent(self.originalValues, elementId)
                    createIfAbsent(self.originalValues[elementId], namespace)
                    for var, value in namespaceDic.iteritems():
                        self.originalValues[elementId][namespace][var] = value
                    continue

                createIfAbsent(self.comVals, namespace)

                for (name, value) in namespaceDic.iteritems():
                    if name in self.comVals[namespace]:
                        if self.comVals[namespace][name] != value:
                            self.comVals[namespace][name] = None
                    else:
                        self.comVals[namespace][name] = value
            else:
                if name in self.comVals:
                    if self.comVals[name] != value:
                        self.comVals[name] = None
                else:
                    self.comVals[name] = value

    def updateContent(self, element):
        _id = element.get('id', '')

        if _id in self.originalValues:
            savedLabel = self.label.copy()
            for namespace, namespaceDic in self.originalValues[_id].iteritems():
                createIfAbsent(self.label, namespace)
                for var, value in namespaceDic.iteritems():
                    self.label[namespace][var] = value

        style = self.generateStyle(self.label)

        self.updateNodeSvgAttributes(element, self.label, style)

        # restore the label before unloading it in the default values
        if _id in self.originalValues:
            self.label = savedLabel.copy()

    def fillResultsPreHook(self):
        if self.namespacesToDelete == 'all':
            self.comVals.clear()
        else:
            for ns in self.namespacesToDelete:
                delWithoutExcept(self.comVals, ns)

    def getValue(self, ns, key, default):
        return self.defVals.get(self.comVals, ns, key, default)

    def setOrDelBool(self, ns, key, bool):
        self.defVals.setOrDelBool(self.comVals, ns, key, bool)

    def setOrDelValue(self, ns, key, value, default):
        self.defVals.setOrDelValue(self.comVals, ns, key, value, default)

    def setOrDelBitmap(self, ns, key, bitmap):
        self.defVals.setOrDelBitmap(self.comVals, ns, key, bitmap)

    def setOrDelColor(self, ns, key, color):
        self.defVals.setOrDelColor(self.comVals, ns, key, color)

    # the methods to implement in children
    def effectLoadHook(self):
        return (False, True)

    def effectUnloadHook(self):
        return True

    def getUserChanges(self):
        return self.comVals
