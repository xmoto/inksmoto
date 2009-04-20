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

from inksmoto.inkex import addNS
from inksmoto.xmotoExtension import XmExt
from inksmoto import log

class XmotoCopy(XmExt):
    def effectHook(self):
        if len(self.selected) != 1:
            log.outMsg("You have to only select the object whose you want \
to copy the Xmoto parameters.")
            return False

        node = self.selected[self.options.ids[0]]
        label = node.get(addNS('xmoto_label', 'xmoto'))

        if label is None:
            log.outMsg("The selected object has no Xmoto properties to copy.")
            return False

        node = self.svg.getAndCreateMetadataNode()
        node.set(addNS('saved_xmoto_label', 'xmoto'), label)

        return False

def run():
    ext = XmotoCopy()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
