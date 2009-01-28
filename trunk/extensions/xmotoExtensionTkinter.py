from xmotoExtension import XmExt
from xmotoTools import createIfAbsent, applyOnElements
from inkex import addNS
import xmGui

class XmExtTkLevel(XmExt):
    """ update level's properties
    """
    def setMetaData(self):
        try:
            self.updateLabelData()
        except Exception, e:
            xmGui.errorMessageBox(e)
            return

        xmGui.quit()

        self.unparseLabel()

        if self.description is not None:
            self.description.text = self.labelValue
        else:
            self.svg.createMetadata(self.labelValue)

    def effect(self):
        self.svg.setDoc(self.document)

        (self.description, self.labelValue) = self.svg.getMetaData()
        self.parseLabel(self.labelValue)

        self.createWindow()
        xmGui.defineOkCancelButtons(command=self.setMetaData)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
        else:
            xmGui.mainLoop()

        self.afterHook()

    def afterHook(self):
        pass

    def createWindow(self):
        pass

    def updateLabelData(self):
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

    def addPath(self, path):
        # put None if a value is different in at least two path
        xmotoLabel = path.get(addNS('xmoto_label', 'xmoto'), '')
        self.parseLabel(xmotoLabel)

        elementId = path.get('id', '')
        for name, value in self.label.iteritems():
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

        self.unparseLabel()

        self.generateStyle()
        self.unparseStyle()

        self.updateNodeSvgAttributes(element)

        if _id in self.originalValues:
            self.label = savedLabel.copy()

    def effectUnloadHook(self):
        return True

    def okPressed(self):
        if self.effectUnloadHook() == True:
            try:
                self.label = self.getUserChanges()
            except Exception, e:
                xmGui.errorMessageBox(e)
                xmGui.quit()
                return

            applyOnElements(self, self.selected, self.updateContent)
            self.unloadDefaultValues()

        xmGui.quit()

    def effectLoadHook(self):
        return (False, True)

    def effect(self):
        if len(self.selected) == 0:
            return

        self.svg.setDoc(self.document)

        (_quit, applyNext) = self.effectLoadHook()
        if _quit == True:
            return
        if applyNext == True:
            self.loadDefaultValues()
            applyOnElements(self, self.selected, self.addPath)

        self.createWindow()
        xmGui.defineOkCancelButtons(command=self.okPressed)

        import testcommands
        if len(testcommands.testCommands) != 0:
            for cmd in testcommands.testCommands:
                exec(cmd)
        else:
            xmGui.mainLoop()

    # the two methods to implement in child
    def createWindow(self):
        pass

    def getUserChanges(self):
        pass
