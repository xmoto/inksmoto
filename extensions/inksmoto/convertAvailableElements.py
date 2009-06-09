#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import log, logging
from parsers import XMLParser

def handleBitmap(attrs):
    out = ""

    out += "\n'%s': {" % attrs['id']
    for name, value in attrs.iteritems():
        if name == 'id':
            continue
        out += "'%s': '%s', " % (name, value)
    out = out[:-2]
    out  += "}, "

    return out

def handleVersion(attrs):
    out = ""

    version = str((int(attrs['versionx']),
                   int(attrs['versiony']),
                   int(attrs['versionz'])))
    if 'function' in attrs:
        function = attrs['function']
        out += "\n'%s': %s, " % (function, version)
    elif 'namespace' in attrs:
        namespace = attrs['namespace']
        variable = attrs['variable']
        out += "\n('%s', '%s'): %s, " % (namespace, variable, version)

    return out

class ElementsXMLParser(XMLParser):
    def parse(self, xmlContent):
        from lxml.etree import XML

        out = ""
        dom = XML(xmlContent)
        dom_head = dom.xpath("//xmoto")[0]

        for child in dom_head:
            groupName = child.tag
            out += "%s = " % groupName.upper()
            out += self.getGroupContent(child)

        return out

    def getGroupContent(self, node):
        out = ""
        useDict = False

        for child in node:
            try:
                attrs = child.attrib

                if 'file' in attrs:
                    useDict = True
                    out += handleBitmap(attrs)
                elif 'versionx' in attrs:
                    useDict = True
                    out += handleVersion(attrs)
                else:
                    out += "'%s', " % attrs['id']
            except Exception, e:
                logging.info("Exception while getting groups content.\n%s" % e)

        # remove last ','
        out = out[:-2]

        if useDict == True:
            out = "{" + out + "}\n"
        else:
            out = "[" + out + "]\n"

        return out

def fromXML(xmlContent):
    parser = ElementsXMLParser()
    return parser.parse(xmlContent)
