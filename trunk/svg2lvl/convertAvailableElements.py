
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

    print out

def fromXML(xmlFile):
    from xml.dom.ext.reader.Sax2 import Reader

    reader = Reader()
    doc = reader.fromStream(xmlFile)
    xmlFile.close()

    out = ""
