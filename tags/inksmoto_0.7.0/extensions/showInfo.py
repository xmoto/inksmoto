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

import sys
from inksmoto.xmotoExtension import XmExt
from inksmoto.xmotoTools import getValue

class ShowInfo(XmExt):
    def getNewLabel(self, label):
        objectType = getValue(label, 'typeid', default='block')

        # current id is set by applyOnElements
        infos = "%s is a %s\n" % (self._id, objectType)
        for key, value in label.iteritems():
            if type(value) == dict:
                if key == 'param':
                    for key, value in value.iteritems():
                        infos += "\tparam name=%s value=%s\n" % (key, value)
                else:
                    infos += "\t%s\n" % key
                    for key, value in value.iteritems():
                        infos += "\t\t%s=%s\n" % (key, value)

        sys.stderr.write(infos)

        return label

def run():
    ext = ShowInfo()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
