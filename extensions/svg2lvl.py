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

from inksmoto import log
import logging
from inksmoto.factory import Factory
from inksmoto.xmotoTools import getTempDir
from os.path import join
from shutil  import copyfile
from inksmoto.inkex   import NSS
# register parsers in the factory
from inksmoto import parsers

def svg2lvl(svgFileName, lvlFileName=None):
    #log.eraseLogFile()

    # save the svg into ~/.inkscape
    lastName = join(getTempDir(), 'last.svg')
    try:
        copyfile(svgFileName, lastName)
    except Exception as e:
        logging.info("Last svg not saved in %s.\n%s" % (lastName, e))

    parser = Factory().create('XmlSvg_parser')

    svgFile = open(svgFileName, 'r')
    level = parser.parse(svgFile)

    if lvlFileName != None:
        lvlfile = open(lvlFileName, 'wb')
    else:
        lvlfile = None
    level.generateLvlContent(lvlfile)

    svgFile.close()
    if lvlfile is not None:
        lvlfile.close()

if __name__ == "__main__":
    import sys
    NSS['xmoto'] = 'http://xmoto.tuxfamily.org/'

    try:
        svg2lvl(sys.argv[-1])
    except Exception as exc:
        log.outMsg(str(exc))
