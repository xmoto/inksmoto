from convertAvailableElements import fromXML
from updateInx import updateInx
from xmotoExtension import XmotoExtension
import sys

class refreshMenu(XmotoExtension):
    def __init__(self):
        XmotoExtension.__init__(self)
        self.OptionParser.add_option("--xml", type="string", dest="xml", 
                                     help="xml file")

    def effect(self):
        dir = self.getInkscapeExtensionsDir()
        
        if self.options.xml in [None, '', 'None']:
            xmlFile = open(dir + '/listAvailableElements.xml', 'r')
        else:
            xmlFile = open(self.options.xml, 'r')

        # update the listAvailableElements.py file with the infos from the xml
        content = fromXML(xmlFile)
        # update the inx files with the infos from the listAvailableElements.py file
        updateInx(content, dir)

        infos = "Please restart Inkscape to update the X-Moto menus."
        sys.stderr.write(infos)

e = refreshMenu()
e.affect()
