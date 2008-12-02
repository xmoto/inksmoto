import logging, log

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
    out += '</xmoto>\n'

    return out

def fromXML(xmlContent):

    from parsers import XMLParser

    class elementsXMLParser(XMLParser):
        def __init__(self):
            pass

        def parse(self, xmlContent):
            from lxml.etree import Element, XML

            out = ""
	    dom = XML(xmlContent)
            dom_head = dom.xpath("//xmoto")[0]

            for child in dom_head:
                groupName = child.tag
                out += "%s=" % groupName
                out += self.getGroupContent(child)

            return out

        def getGroupContent(self, node):
            out = ""
            useDict = False

            for child in node:
                try:
                    attrs = self.getNodeAttributes(child)

                    if 'file' in attrs:
                        useDict = True
                        out += "\n'" + attrs['id'] + "': {"
                        for name, value in attrs.iteritems():
                            if name == 'id':
                                continue
                            out += "'" + name + "': '" + value + "',"
                        out = out[:-1]
                        out  += "},"
                    else:
                        out += "'" + attrs['id'] + "',"
                except:
                    pass

            # remove last ','
            out = out[:-1]
            if useDict == True:
                out = "{" + out + "}\n"
            else:
                out = "[" + out + "]\n"
            return out

    parser = elementsXMLParser()
    return parser.parse(xmlContent)
