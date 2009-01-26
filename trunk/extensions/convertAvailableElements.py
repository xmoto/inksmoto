from parsers import XMLParser
import logging

def handleBitmap(attrs):
    out = ""

    out += "\n'%s': {" % attrs['id']
    for name, value in attrs.iteritems():
        if name == 'id':
            continue
        out += "'%s': '%s'," % (name, value)
    out = out[:-1]
    out  += "},"

    return out

def handleVersion(attrs):
    out = ""

    version = str((int(attrs['versionx']),
                   int(attrs['versiony']),
                   int(attrs['versionz'])))
    if 'function' in attrs:
        function = attrs['function']
        out += "\n'%s': %s," % (function, version)
    elif 'namespace' in attrs:
        namespace = attrs['namespace']
        variable = attrs['variable']
        out += "\n('%s', '%s'): %s," % (namespace, variable, version)

    return out

class ElementsXMLParser(XMLParser):
    def parse(self, xmlContent):
        from lxml.etree import XML

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
                    out += handleBitmap(attrs)
                elif 'versionx' in attrs:
                    useDict = True
                    out += handleVersion(attrs)
                else:
                    out += "'%s'," % attrs['id']
            except Exception, e:
                logging.info("Exception while getting groups content.\n%s" % e)

        # remove last ','
        out = out[:-1]

        if useDict == True:
            out = "{" + out + "}\n"
        else:
            out = "[" + out + "]\n"

        return out

def fromXML(xmlContent):
    parser = ElementsXMLParser()
    return parser.parse(xmlContent)
