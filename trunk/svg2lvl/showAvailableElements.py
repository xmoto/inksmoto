from xmotoExtension import XmotoExtension
import listAvailableElements
import sys

class ShowAvailableElements(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)

    def effect(self):
        infos = "Available textures:\n"
        for texture in listAvailableElements.textures:
            infos += "\t%s\n" % texture
        infos += "Available edge textures:\n"
        for edgeTexture in listAvailableElements.edgeTextures:
            infos += "\t%s\n" % edgeTexture
        infos += "Available particle sources:\n"
        for particleSource in listAvailableElements.particleSources:
            infos += "\t%s\n" % particleSource
        infos += "Available sprites:\n"
        for sprite in listAvailableElements.sprites:
            infos += "\t%s\n" % sprite

        sys.stderr.write(infos)

e = ShowAvailableElements()
e.affect()
