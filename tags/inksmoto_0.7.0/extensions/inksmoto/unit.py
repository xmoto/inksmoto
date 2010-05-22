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

import re

def getValueAndUnit(unitValue):
    match = UnitsConvertor.program.match(unitValue)
    # first group is the float, and fifth group is the unit
    unit = match.group(5)
    if unit is None:
        unit = 'px'
    return float(match.group(1)), unit

class UnitsConvertor:    
    convertToPx = {'cm': 35.43,
                   'ft': 1076.0,
                   'in': 89.96,
                   'm' : 3500.0,
                   'mm': 3.543,
                   'pc': 15.0,
                   'pt': 1.25,
                   'px': 1.0}

    convertFromPx = {'cm': 0.028224,
                     'ft': 0.000929,
                     'in': 0.011116,
                     'm' : 0.000285,
                     'mm': 0.282246,
                     'pc': 0.066666,
                     'pt': 0.8,
                     'px': 1.0}

    r = r'([-+]?(\d+(\.\d*)?|\d*\.\d+)([eE][-+]?\d+)?)(cm|ft|in|mm|m|pc|pt|px)?'
    program = re.compile(r)

    def __init__(self, *args):
        if len(args) > 0:
            self.store(args[0])
        else:
            self.value = 0.0

    def store(self, unitValue):
        # store lenght in px
        value, unit = getValueAndUnit(unitValue)
        mult = UnitsConvertor.convertToPx[unit]
        self.value = value * mult

    def convert(self, unit):
        return self.value * UnitsConvertor.convertFromPx[unit]
