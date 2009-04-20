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

from inksmoto.xmotoExtension import XmExt
from inksmoto.inkex import addNS
from inksmoto import log

class XmotoPaste(XmExt):
    def effectHook(self):
        if len(self.selected) == 0:
            log.outMsg("You have to select the objects whose you want to \
paste the Xmoto parameters.")
            return False
        
        descriptionNode = self.svg.getMetaDataNode()
        if descriptionNode is None:
            log.outMsg("You have to copy the Xmoto properties of an \
object first.")
            return False

        label = descriptionNode.get(addNS('saved_xmoto_label', 'xmoto'))

        if label is None:
            log.outMsg("You have to copy the Xmoto properties of an \
object first.")
            return False

        for node in self.selected.values():
            node.set(addNS('xmoto_label', 'xmoto'), label)

        # we want to update the nodes shapes with their new style
        return True

def run():
    ext = XmotoPaste()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
