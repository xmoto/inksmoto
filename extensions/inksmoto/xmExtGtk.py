#!/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

import logging
from gi.repository import Gtk, Gdk, GdkPixbuf
from .xmotoExtension import XmExt
from .defaultValues import DefaultValues
from .xmotoTools import createIfAbsent, applyOnElements, delWoExcept
from .xmotoTools import getExistingImageFullPath, conv8to16, conv16to8
from .xmotoTools import setOrDelBool, setOrDelValue, setOrDelColor, getValue
from .xmotoTools import setOrDelBitmap, getIndexInList
from .inkex import addNS
from .parsers import LabelParser
from . import xmGuiGtk
from inksmoto.availableElements import AvailableElements
from .testsCreator import TestsCreator
from inksmoto.confGenerator import Conf
from os.path import exists

class WidgetInfos:
    def __init__(self, ns, key, default=None, accessors=None,
                 items=None, dontDel=False):
        self.ns = ns
        self.key = key
        self.default = default
        self.accessors = accessors
        self.items = items
        self.dontDel = dontDel

    def get(self):
        return (self.ns, self.key, self.default, self.accessors,
                self.items, self.dontDel)

class XmExtGtk(XmExt):
    def __init__(self):
        super().__init__()
        self.widgets = {}

    def createWindow(self, okFunc):
        def addLog(command, widget, buttonCmd):
            if Conf()['enableRecording']:
                TestsCreator().addGtkCmd(buttonCmd)
            command(widget)

        (gladeFile, self.windowName) = self.getWindowInfos()
        
        # Assign the builder to self.wTree (the returned value from createWindow)
        self.wTree = xmGuiGtk.createWindow(gladeFile, self.windowName)
        
        # Now, use the builder to get the window
        window = self.get(self.windowName)
        
        # Ensure window is found, if not log an error or handle it
        if window:
            window.connect("destroy", xmGuiGtk.quit)
        else:
            logging.error(f"Window '{self.windowName}' not found.")

        # Set up the signal handlers
        _dic = {"on_apply_clicked": lambda widget:
                    addLog(okFunc, widget, "self.get('apply').clicked()"),
                "on_cancel_clicked": lambda widget:
                    addLog(xmGuiGtk.quit, widget, "self.get('cancel').clicked()")}
        
        signals = self.getSignals()
        if signals is not None:
            signals.update(_dic)
            self.wTree.connect_signals(signals)

        self.widgetsInfos = self.getWidgetsInfos()
        if self.widgetsInfos is not None:
            if self.recording:
                self.addTraces(self.widgetsInfos)

            self.fillWindowValues(self.widgetsInfos)
            self.getSignals()
    def mainLoop(self):
        from . import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
            # has Gtk.main() has not been called, Gtk.main_quit()
            # doesn’t work for destroying the window. destroy it manually
            self.get(self.windowName).destroy()
        else:
            xmGuiGtk.mainLoop()

    def addWidget(self, widgetName, widget):
        self.widgets[widgetName] = widget

    def get(self, widgetName):
        file_handler = logging.FileHandler('/tmp/inkscape_extension.log')
        file_handler.setLevel(logging.DEBUG)

        # Create a logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Add the file handler
        logger.addHandler(file_handler)
        # Retrieve the GtkBox or GtkGrid object from the Glade file
        widget = self.wTree.get_object(widgetName)
        if widget is None:
            logger.debug(f"Widget: {widget} is none for Widget Name: {widgetName}")
            file_handler.flush()
        if widget is None and widgetName in self.widgets:
            widget = self.widgets[widgetName]
        return widget

    def registerSignals(self, signals):
        self.wTree.connect_signals(signals)


    def fillWindowValues(self, values):
        """ get a dict with 'widgetName': (ns, key, default,
            accessors). For each widget in the dict, get the value
            from the svg and set it to the widget
        """
        for widgetName, widgetInfos in values.items():
            (ns, key, default, accessors, items, dontDel) = widgetInfos.get()
            value = self.getValue(ns, key, default)
            widget = self.get(widgetName)

            if isinstance(widget, Gtk.CheckButton):
                widget.set_active(value == 'true')
            elif isinstance(widget, Gtk.Scale):
                if value is not None:
                    if accessors is not None:
                        setter, _ = accessors
                        value = setter(float(value))
                    widget.set_value(float(value))
            elif isinstance(widget, Gtk.Button):
                label = self.get(widgetName + 'Label')
                if label is not None:
                    imgName = value
                    bitmapDict = None
                    img = None
                    for type_ in ['TEXTURES', 'EDGETEXTURES', 'PARTICLESOURCES', 'SPRITES']:
                        try:
                            bitmapDict = AvailableElements()[type_]
                            img = bitmapDict[imgName]['file']
                        except KeyError:
                            pass
                        else:
                            break
                    if img is not None:
                        xmGuiGtk.addImgToBtn(widget, label, imgName, bitmapDict)
            elif isinstance(widget, Gtk.ColorButton):
                r = self.getValue(ns, key + '_r', default)
                g = self.getValue(ns, key + '_g', default)
                b = self.getValue(ns, key + '_b', default)
                a = self.getValue(ns, key + '_a', default)
                widget.set_rgba(Gdk.RGBA(float(r) / 255.0, float(g) / 255.0, float(b) / 255.0, float(a) / 255.0))
            elif isinstance(widget, Gtk.Entry):
                widget.set_text(value)
            elif isinstance(widget, Gtk.FileChooserButton):
                if exists(value):
                    widget.set_filename(value)
            elif isinstance(widget, Gtk.ComboBox):
                listStore = Gtk.ListStore(str)
                widget.set_model(listStore)
                cell = Gtk.CellRendererText()
                widget.pack_start(cell, True)
                widget.add_attribute(cell, 'text', 0)

                for item in items:
                    widget.append_text(item)
                selection = getIndexInList(items, value)
                widget.set_active(selection)
    def fillResults(self, dict_):
        if self.widgetsInfos is None:
            return

        self.fillResultsPreHook()

        for widgetName in list(self.widgetsInfos.keys()):
            widget = self.get(widgetName)
            (ns, key, default, accessors, items, dontDel) = self.widgetsInfos[widgetName].get()
            createIfAbsent(dict_, ns)

            if isinstance(widget, Gtk.CheckButton):
                bool_ = widget.get_active()
                self.setOrDelBool(ns, key, bool_, dontDel)
            elif isinstance(widget, Gtk.Scale):
                value = widget.get_value()
                if accessors is not None:
                    _, getter = accessors
                    value = getter(value)
                self.setOrDelValue(ns, key, value, default)
            elif isinstance(widget, Gtk.Button):
                label = self.get(widgetName + 'Label')
                if label is not None:
                    bitmap = label.get_text()
                    self.setOrDelBitmap(ns, key, bitmap)
            elif isinstance(widget, Gtk.ColorButton):
                color = widget.get_rgba()
                (r, g, b, a) = (int(color.red * 255),
                                int(color.green * 255),
                                int(color.blue * 255),
                                int(color.alpha * 255))
                self.setOrDelColor(ns, key, (r, g, b, a))
            elif isinstance(widget, Gtk.Entry):
                text = widget.get_text()
                self.setOrDelValue(ns, key, text, default)
            elif isinstance(widget, Gtk.FileChooserButton):
                fileName = widget.get_filename()
                self.setOrDelValue(ns, key, fileName, default)
            elif isinstance(widget, Gtk.ComboBox):
                music = widget.get_active_text()
                self.setOrDelValue(ns, key, music, default)

        self.removeUnusedNs(dict_)

    def removeUnusedNs(self, dict_):
        toDel = []
        for ns in dict_.keys():
            if dict_[ns] == {}:
                toDel.append(ns)
        for ns in toDel:
            del dict_[ns]

    def addTraces(self, widgets):
        def _log(f, widgetName, paramType):
            def __log(*args, **kw):
                ret = f(*args, **kw)
                logger(f, widgetName, paramType, args, kw, ret)
                return ret
            return __log

        logger = traceCalls

        for widgetName, widgetInfos in widgets.items():
            (ns, key, default, accessors, items, dontDel) = widgetInfos.get()
            widget = self.get(widgetName)
            if isinstance(widget, Gtk.CheckButton):
                get_active = getattr(widget, 'get_active')
                setattr(widget, 'get_active',
                        _log(get_active, widgetName, paramType=bool))
            elif isinstance(widget, Gtk.Scale):
                get_value = getattr(widget, 'get_value')
                setattr(widget, 'get_value',
                        _log(get_value, widgetName, paramType=float))
            elif isinstance(widget, Gtk.Button):
                labelName = widgetName + 'Label'
                label = self.get(labelName)
                if label is not None:
                    get_text = getattr(label, 'get_text')
                    setattr(label, 'get_text',
                            _log(get_text, labelName, paramType=str))
            elif isinstance(widget, Gtk.ColorButton):
                get_rgba = getattr(widget, 'get_rgba')
                setattr(widget, 'get_rgba',
                        _log(get_rgba, widgetName, paramType=Gdk.RGBA))
            elif isinstance(widget, Gtk.Entry):
                get_text = getattr(widget, 'get_text')
                setattr(widget, 'get_text',
                        _log(get_text, widgetName, paramType=str))
            elif isinstance(widget, Gtk.FileChooserButton):
                get_filename = getattr(widget, 'get_filename')
                setattr(widget, 'get_filename',
                        _log(get_filename, widgetName, paramType=str))
            elif isinstance(widget, Gtk.ComboBox):
                get_active = getattr(widget, 'get_active')
                setattr(widget, 'get_active',
                        _log(get_active, widgetName, paramType=int))

class XmExtGtkElement(XmExtGtk):
    def __init__(self):
        super().__init__()
        self.namespacesToDelete = []
        self.originalValues = {}
        self.defVals = DefaultValues()

    def okPressed(self, widget=None):
        if self.effectUnloadHook():
            try:
                self.fillResults(self.comVals)
                self.label = self.getUserChanges()
            except Exception as e:
                logging.error(str(e))
                xmGuiGtk.errorMessageBox(str(e))
                return

            applyOnElements(self, self.selected, self.updateContent)
            self.defVals.unload(self.label)

        xmGuiGtk.quit()

    def effect(self):
        """ Load the selected objects, create the window, and set the widgets' values. """
        if len(self.selected) == 0:
            return

        self.svg.setDoc(self.document)

        (_quit, applyNext) = self.effectLoadHook()
        if _quit:
            return
        if applyNext:
            self.defVals.load(self.svg)
            applyOnElements(self, self.selected, self.addPath)

        self.createWindow(self.okPressed)

        self.mainLoop()

    def addPath(self, path):
        # Put None if a value is different in at least two paths
        label = path.get(addNS('xmoto_label', 'xmoto'), '')
        label = LabelParser().parse(label)

        self.defVals.addElementLabel(label)

        elementId = path.get('id', '')
        for name, value in label.items():
            if isinstance(value, dict):
                namespace = name
                namespaceDic = value

                # Save original xmotoLabel to put back parameters not modified by this extension
                if self.namespacesInCommon is not None and namespace not in self.namespacesInCommon:
                    createIfAbsent(self.originalValues, elementId)
                    createIfAbsent(self.originalValues[elementId], namespace)
                    for var, value in namespaceDic.items():
                        self.originalValues[elementId][namespace][var] = value
                    continue

                createIfAbsent(self.comVals, namespace)

                for name, value in namespaceDic.items():
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
            for namespace, namespaceDic in self.originalValues[_id].items():
                createIfAbsent(self.label, namespace)
                for var, value in namespaceDic.items():
                    self.label[namespace][var] = value

        style = self.generateStyle(self.label)

        self.updateNodeSvgAttributes(element, self.label, style)

        # Restore the label before unloading it in the default values
        if _id in self.originalValues:
            self.label = savedLabel.copy()

    def fillResultsPreHook(self):
        if self.namespacesToDelete == 'all':
            self.comVals.clear()
        else:
            for ns in self.namespacesToDelete:
                delWoExcept(self.comVals, ns)

    def getValue(self, ns, key, default):
        return self.defVals.get(self.comVals, ns, key, default)

    def setOrDelBool(self, ns, key, bool, dontDel=False):
        self.defVals.setOrDelBool(self.comVals, ns, key, bool)

    def setOrDelValue(self, ns, key, value, default):
        self.defVals.setOrDelValue(self.comVals, ns, key, value, default)

    def setOrDelBitmap(self, ns, key, bitmap):
        self.defVals.setOrDelBitmap(self.comVals, ns, key, bitmap)

    def setOrDelColor(self, ns, key, color):
        self.defVals.setOrDelColor(self.comVals, ns, key, color)

    # Methods to implement in children
    def effectLoadHook(self):
        return (False, True)

    def effectUnloadHook(self):
        return True

    def getUserChanges(self):
        return self.comVals