from parsers import LabelParser
from xmotoTools import getValue, setOrDelBool, setOrDelBitmap
from xmotoTools import delWithoutExcept, updateInfos
from inkex import addNS

class DefaultValues:
    def __init__(self):
        self.defaultValues = {}
        self.svg = None

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
            value = getValue(self.defaultValues, namespace, name, None)
            if value is None:
                return default
            else:
                return value
        else:
            return value

    def setOrDelBool(self, _dict, namespace, widget, key):
        if setOrDelBool(_dict[namespace], widget, key) == False:
            delWithoutExcept(self.defaultValues, key, namespace)

    def setOrDelBitmap(self, _dict, namespace, key, button):
        if setOrDelBitmap(_dict[namespace], key, button) == False:
            delWithoutExcept(self.defaultValues, key, namespace)

