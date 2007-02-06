
def toXML():
    import listAvailableElements

    def fillFromDict(name, dicValue):
        out = "\t<%ss>\n" % name
        for key, value in dicValue.items():
            out += "\t\t<%s id=\"%s\"" % (name, key)
            for key, value in value.items():
                out += " %s=\"%s\"" % (key, value)
            out += "/>\n"
        out += "\t</%ss>\n" % name
        return out

    def fillFromList(name, listValue):
        out = "\t<%ss>\n" % name
        for edge in listValue:
            out += "\t\t<%s id=\"%s\"/>\n" % (name, edge)
        out += "\t</%ss>\n" % name
        return out

    out = '<xmoto>\n'
    out += fillFromDict('texture', listAvailableElements.textures)
    out += fillFromList('edgeTexture', listAvailableElements.edgeTextures)
    out += fillFromList('particleSource', listAvailableElements.particleSources)
    out += fillFromDict('sprite', listAvailableElements.sprites)
    out += fillFromList('skie', listAvailableElements.skies)
    out += fillFromList('rversion', listAvailableElements.rversions)
    out += '</xmoto>\n'

    return out

def fromXML(xmlContent):

    from parsers import XMLParser

    class elementsXMLParser(XMLParser):
        def __init__(self):
            pass

        def parse(self, xmlContent):
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xmlContent)

            out = ""
            dom_head = dom.getElementsByTagName("xmoto")[0]

            for i in xrange(dom_head.childNodes.length):
                child = dom_head.childNodes.item(i)
                if child.nodeType == child.TEXT_NODE:
                    continue
                groupName = child.nodeName
                out += "%s=" % groupName
                out += self.getGroupContent(child)

            return out

        def getGroupContent(self, node):
            out = ""
            out += "["
            for i in xrange(node.childNodes.length):
                child = node.childNodes.item(i)
                if child.nodeType == child.TEXT_NODE:
                    continue

                attrs = self.getNodeAttributes(child)
                if attrs.has_key('id'):
                    out += "'" + attrs['id'] + "',"

            out = out[:-1]
            out += "]\n"
            return out

    parser = elementsXMLParser()
    return parser.parse(xmlContent)
