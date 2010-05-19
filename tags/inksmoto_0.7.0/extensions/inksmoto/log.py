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

import logging
from os.path import expanduser

LOGFILE = expanduser('~/svg2lvl.log')

try:
    # no log with python 2.3
    logging.basicConfig(filename = LOGFILE,
                        format   = '%(asctime)s %(levelname)s %(message)s',
                        level    = logging.INFO)
except Exception, e:
    pass

def eraseLogFile():
    f = open(LOGFILE, 'w')
    f.close()

def outMsg(msg):
    import sys
    logging.info(msg)
    sys.stderr.write(msg + '\n')
