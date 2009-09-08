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
                    label.set_text(value)
                    img = None
                    for type in ['TEXTURES', 'EDGETEXTURES',
                                 'PARTICLESOURCES', 'SPRITES']:
                        try:
                            img = AvailableElements()[type][value]['file']
                        except:
                            pass
                        else:
                            break
                    if img is not None:
                        imgFile = getExistingImageFullPath(img)
                        xmGuiGtk.addImageToButton(widget, imgFile)
            elif widget.__class__ == gtk.ColorButton:
                # ColorButton
                r = self.defVals.get(self.comVals, ns, key+'_r', default)
                g = self.defVals.get(self.comVals, ns, key+'_g', default)
                b = self.defVals.get(self.comVals, ns, key+'_b', default)
                a = self.defVals.get(self.comVals, ns, key+'_a', default)
                widget.set_color(gtk.gdk.Color(conv8to16(int(r)),
                                               conv8to16(int(g)),
                                               conv8to16(int(b))))
                widget.set_alpha(conv8to16(int(a)))
            elif widget.__class__ == gtk.Entry:
                widget.set_text(value)
            elif widget.__class__ == gtk.FileChooserButton:
                widget.set_filename(value)

    def fillResults(self):
        """ for each widget, fill the self.comVals with its value.
            it first delete some namespaces to be more clean
        """
        import gtk
        results = {}

        if self.widgetsInfos is None:
            return results
        
        for widgetName in self.widgetsInfos.keys():
            widget = self.wTree.get_widget(widgetName)
            (ns, key, default, accessors) = self.widgetsInfos[widgetName]

            if widget.__class__ == gtk.CheckButton:
                results[widgetName] = (gtk.CheckButton, widget.get_active())
            elif widget.__class__ == gtk.HScale:
                value = widget.get_value()
                if accessors is not None:
                    (setter, getter) = accessors
                    value = getter(value)
                results[widgetName] = (gtk.HScale, value)
            elif widget.__class__ == gtk.Button:
                label = self.get(widgetName+'Label')
                if label is not None:
                    bitmap = label.get_text()
                    results[widgetName] = (gtk.Button, bitmap)
            elif widget.__class__ == gtk.ColorButton:
                color = widget.get_color()
                (r, g, b) = (conv16to8(color.red),
                             conv16to8(color.green),
                             conv16to8(color.blue))
                a = conv16to8(widget.get_alpha())
                results[widgetName] = (gtk.ColorButton, (r, g, b, a))
            elif widget.__class__ == gtk.Entry:
                text = widget.get_text()
                results[widgetName] = (gtk.Entry, text)
            elif widget.__class__ == gtk.FileChooserButton:
                fileName = widget.get_filename()
                results[widgetName] = (gtk.FileChooserButton, fileName)
        return results

    def removeUnusedNs(self, dict):
        toDel = []
        for ns in dict.iterkeys():
            if dict[ns] == {}:
                toDel.append(ns)
        for ns in toDel:
            del dict[ns]

    def getWindowInfos(self):
        return None

    def getSignals(self):
        return None

    def storeResults(self, results):
        pass

    def getValue(self, ns, key, default):
        return None

class XmExtGtkLevel(XmExtGtk):
    """ update level's properties
    """
    def load(self):
        (self.node, metadata) = self.svg.getMetaData()
        self.label = LabelParser().parse(metadata)

    def store(self, widget):
        results = self.fillResults()
        self.storeResults(results)
        self.updateLabelData()
        try:
            results = self.fillResults()
            self.storeResults(results)
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

    def storeResults(self, results):
        import gtk

        if self.widgetsInfos is None:
            return

        for widgetName in self.widgetsInfos.keys():
            (ns, key, default, accessors) = self.widgetsInfos[widgetName]
            if widgetName not in results:
                continue
            (wClass, result) = results[widgetName]
            createIfAbsent(self.label, ns)

            if wClass == gtk.CheckButton:
                setOrDelBool(self.label[ns], key, result)
            elif wClass == gtk.ColorButton:
                setOrDelColor(self.label[ns], key, result)
            else:
                setOrDelValue(self.label[ns], key, result, default)

        self.removeUnusedNs(self.label)

    def getValue(self, ns, key, default):
        return getValue(self.label, ns, key, default)

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
                results = self.fillResults()
                self.storeResults(results)
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

    def storeResults(self, results):
        import gtk

        if self.widgetsInfos is None:
            return

        if self.namespacesToDelete == 'all':
            self.comVals = {}
        else:
            for ns in self.namespacesToDelete:
                delWithoutExcept(self.comVals, ns)

        for widgetName in self.widgetsInfos.keys():
            (ns, key, default, accessors) = self.widgetsInfos[widgetName]
            if widgetName not in results:
                continue
            (wClass, result) = results[widgetName]
            createIfAbsent(self.comVals, ns)

            if wClass == gtk.CheckButton:
                self.defVals.setOrDelBool(self.comVals, ns, key, result)
            elif wClass == gtk.HScale:
                self.defVals.setOrDelValue(self.comVals, ns, key,
                                           result, default)
            elif wClass == gtk.Button:
                self.defVals.setOrDelBitmap(self.comVals, ns, key, result)
            elif wClass == gtk.ColorButton:
                self.defVals.setOrDelColor(self.comVals, ns, key, result)

        self.removeUnusedNs(self.comVals)

    def getValue(self, ns, key, default):
        return self.defVals.get(self.comVals, ns, key, default)

    # the methods to implement in children
    def effectLoadHook(self):
        return (False, True)

    def effectUnloadHook(self):
        return True

    def getUserChanges(self):
        return self.comVals
