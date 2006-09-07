import re
import logging, log

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

    program = re.compile('([-+]?(\d+(\.\d*)?|\d*\.\d+)([eE][-+]?\d+)?)(cm|ft|in|mm|m|pc|pt|px)')

    def __init__(self, *args):
        if len(args) > 0:
            self.store(args[0])

    def getValueAndUnit(self, unitValue):
        match = UnitsConvertor.program.match(unitValue)
        # first group is the float, and fifth group is the unit
        return float(match.group(1)), match.group(5)

    def store(self, unitValue):
        # store lenght in px
        value, unit = self.getValueAndUnit(unitValue)
        mult = UnitsConvertor.convertToPx[unit]
        self.value = value * mult

    def convert(self, unit):
        return self.value * UnitsConvertor.convertFromPx[unit]
