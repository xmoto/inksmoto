from xmotoExtension import XmExt
from xmotoTools import createIfAbsent, applyOnElements
from inkex import addNS
import xmGui
from defaultValues import DefaultValues
from parsers import LabelParser

import log, logging, sys

class XmExtTk(XmExt):
    """ do not update the svg
    """
    def effect(self):
        self.svg.setDoc(self.document)

        self.createWindow()
        xmGui.defineOkCancelButtons(command=self.apply)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd, globals(), locals())
        else:
            xmGui.mainLoop()

    # the two methods to implement in children
    def apply(self):
        xmGui.quit()

    def createWindow(self):
        pass

class XmExtTkLevel(XmExt):
    """ update level's properties
    """
    def load(self):
        (self.node, metadata) = self.svg.getMetaData()
        self.label = LabelParser().parse(metadata)

    def store(self):
        try:
            self.updateLabelData()
        except Exception, e:
            xmGui.errorMessageBox(e)
            return

        xmGui.quit()

        metadata = LabelParser().unparse(self.label)

        if self.node is not None:
            self.node.text = metadata
        else:
            self.svg.createMetadata(metadata)

    def effect(self):
        self.svg.setDoc(self.document)

        self.load()

        self.createWindow()
        xmGui.defineOkCancelButtons(command=self.store)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd, globals(), locals())
        else:
            xmGui.mainLoop()

        self.afterHook()

    # the three methods to implements in child
    def createWindow(self):
        pass

    def updateLabelData(self):
        pass

    def afterHook(self):
        pass

class XmExtTkElement(XmExt):
    """ update elements' properties
    """
    def __init__(self):
        XmExt.__init__(self)
        # the dictionnary which contains the elements informations
        self.commonValues = {}
        self.namespacesInCommon = None
        self.originalValues = {}
        self.defaultValues = DefaultValues()

    def addPath(self, path):
        # put None if a value is different in at least two path
        label = path.get(addNS('xmoto_label', 'xmoto'), '')
        label = LabelParser().parse(label)

        self.defaultValues.addElementLabel(label)

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

                createIfAbsent(self.commonValues, namespace)

                for (name, value) in namespaceDic.iteritems():
                    if name in self.commonValues[namespace]:
                        if self.commonValues[namespace][name] != value:
                            self.commonValues[namespace][name] = None
                    else:
                        self.commonValues[namespace][name] = value
            else:
                if name in self.commonValues:
                    if self.commonValues[name] != value:
                        self.commonValues[name] = None
                else:
                    self.commonValues[name] = value

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

        if _id in self.originalValues:
            self.label = savedLabel.copy()

    def okPressed(self):
        if self.effectUnloadHook() == True:
            try:
                self.label = self.getUserChanges()
            except Exception, e:
                xmGui.errorMessageBox(e)
                xmGui.quit()
                return

            applyOnElements(self, self.selected, self.updateContent)
            self.defaultValues.unload(self.label)

        xmGui.quit()

    def effect(self):
        if len(self.selected) == 0:
            return

        self.svg.setDoc(self.document)

        (_quit, applyNext) = self.effectLoadHook()
        if _quit == True:
            return
        if applyNext == True:
            self.defaultValues.load(self.svg)
            applyOnElements(self, self.selected, self.addPath)

        self.createWindow()
        xmGui.defineOkCancelButtons(command=self.okPressed)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
        else:
            xmGui.mainLoop()

    # the four methods to implement in children
    def effectLoadHook(self):
        return (False, True)

    def createWindow(self):
        pass

    def effectUnloadHook(self):
        return True

    def getUserChanges(self):
        pass
