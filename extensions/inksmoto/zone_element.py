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

from factory  import Factory
from elements import Element

class Zone(Element):
    def writeContent(self, options, level):
        """
        <zone id="FirstZone">
                <box left="-29.0" right="-17.0" top="6.0" bottom="0.0"/>
        </zone>
        """
        self.newWidth  = options['width']
        self.newHeight = options['height']
        self.ratio     = options['ratio']

        self.preProcessVertex()
        maxX, minY = self.pointInLevelSpace(self.aabb.xmax, self.aabb.ymax)
        minX, maxY = self.pointInLevelSpace(self.aabb.xmin, self.aabb.ymin)

        self.content.append("\t<zone id=\"%s\">" % (self._id))
        line = "\t\t<box left=\"%f\" right=\"%f\" top=\"%f\" bottom=\"%f\"/>"
        self.content.append(line % (minX, maxX, maxY, minY))

        self.addElementParams()
        self.content.append("\t</zone>")

        return self.content

def initModule():
    Factory().register('Zone_element', Zone)

initModule()
