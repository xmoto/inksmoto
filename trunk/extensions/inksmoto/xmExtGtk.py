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
from xmotoTools import getExistingImageFullPath, conv8to16, conv16to8
from inkex import addNS
from parsers import LabelParser
import xmGuiGtk
from inksmoto.availableElements import AvailableElements

class XmExtGtkElement(XmExt):
    """ update elements' properties
    """
    def __init__(self):
        XmExt.__init__(self)
        # the dictionnary which contains the elements informations
        self.comVals = {}
        self.namespacesInCommon = None
        self.namespacesToDelete = []
        self.originalValues = {}
        self.defVals = DefaultValues()

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

    def okPressed(self, widget=None):
        if self.effectUnloadHook() == True:
            try:
                self.fillResults()
                self.label = self.getUserChanges()
            except Exception, e:
                logging.error(str(e))
                xmGuiGtk.errorMessageBox(str(e))
                #xmGuiGtk.quit()
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

        (gladeFile, windowName) = self.getWindowInfos()
        self.wTree = xmGuiGtk.createWindow(gladeFile, windowName)
        window = self.get(windowName)
        window.connect("destroy", xmGuiGtk.quit)

        _dic = {"on_apply_clicked" : self.okPressed,
               "on_cancel_clicked" : xmGuiGtk.quit}
        self.wTree.signal_autoconnect(_dic)

        self.widgetsInfos = self.getWidgetsInfos()
        if self.widgetsInfos is not None:
            self.fillWindowValues(self.widgetsInfos)

        signals = self.getSignals()
        if signals is not None:
            self.registerSignals(signals)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
        else:
            xmGuiGtk.mainLoop()

    def get(self, widgetName):
        return self.wTree.get_widget(widgetName)

    def fillResults(self):
        """ for each widget, fill the self.comVals with its value.
            it first delete some namespaces to be more clean
        """
        import gtk

        if self.widgetsInfos is None:
            return

        if self.namespacesToDelete == 'all':
            self.comVals = {}
        else:
            for ns in self.namespacesToDelete:
                delWithoutExcept(self.comVals, ns)

        for widgetName in self.widgetsInfos.keys():
            widget = self.wTree.get_widget(widgetName)
            (ns, key, default, accessors) = self.widgetsInfos[widgetName]
            createIfAbsent(self.comVals, ns)

            if widget.__class__ == gtk.CheckButton:
                self.defVals.setOrDelBool(self.comVals, ns, key,
                                          widget.get_active())
            elif widget.__class__ == gtk.HScale:
                value = widget.get_value()
                if accessors is not None:
                    (setter, getter) = accessors
                    value = getter(value)
                self.defVals.setOrDelValue(self.comVals, ns, key,
                                           value, default)
            elif widget.__class__ == gtk.Button:
                label = self.get(widgetName+'Label')
                if label is not None:
                    bitmap = label.get_text()
                    self.defVals.setOrDelBitmap(self.comVals, ns, key, bitmap)
            elif widget.__class__ == gtk.ColorButton:
                color = widget.get_color()
                (r, g, b) = (conv16to8(color.red),
                             conv16to8(color.green),
                             conv16to8(color.blue))
                a = conv16to8(widget.get_alpha())
                
                self.defVals.setOrDelColor(self.comVals, ns, key, (r, g, b, a))


    def fillWindowValues(self, values):
        """ get a dict with 'widgetName': (ns, key, default). For
            each widget in the dict, get the value from the svg and
            set it to the widget
        """
        import gtk

        for widgetName, (ns, key, default, accessors) in values.iteritems():
            value = self.defVals.get(self.comVals, ns, key, default)
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
                r = self.defVals.get(self.comVals, ns, key+'_r', default)
                g = self.defVals.get(self.comVals, ns, key+'_g', default)
                b = self.defVals.get(self.comVals, ns, key+'_b', default)
                a = self.defVals.get(self.comVals, ns, key+'_a', default)
                widget.set_color(gtk.gdk.Color(conv8to16(int(r)),
                                               conv8to16(int(g)),
                                               conv8to16(int(b))))
                widget.set_alpha(conv8to16(int(a)))

    def registerSignals(self, signals):
        for signal, func in signals.iteritems():
            self.wTree.signal_connect(signal, func)

    # the methods to implement in children
    def effectLoadHook(self):
        return (False, True)

    def getWindowInfos(self):
        return None

    def getWindowValues(self):
        return (None, None)

    def effectUnloadHook(self):
        return True

    def getUserChanges(self):
        return self.comVals

    def getSignals(self):
        return None
