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

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/412551

class Singleton(type):
    def __init__(mcs, *args):
        type.__init__(mcs, *args)
        mcs._instances = {}

    def __call__(mcs, *args):
        if not args in mcs._instances:
            mcs._instances[args] = type.__call__(mcs, *args)
        return mcs._instances[args]

# exemple usage:
#class Test:
#    __metaclass__=Singleton
#    def __init__(self, *args):
#        pass
