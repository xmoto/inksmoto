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

from .singleton import Singleton
from os.path import join, basename
from os import remove, chdir
import sys, glob
from .xmotoTools import getHomeDir, createDirsOfFile
from .confGenerator import Conf
from shutil  import copyfile

class TestsCreator(metaclass=Singleton):
    def __init__(self):
        self.conf = Conf()
        relTestsDir = join('cur_tests', self.conf['recordingSession'])
        self.testsDir = join(getHomeDir(), relTestsDir)
        self.testValues = {'gtkCmds': []}

    def generateTests(self):
        """
        """
        tests = self.getTests()
        sessionId = self.conf['recordingSession']

        testHeader = "\n\
import unittest\n\
import os\n\
from xmotoTestCase import xmotoTestCase, getHomeDir\n\
\n\
def getTestSuite():\n\
    return unittest.makeSuite(Test%s, 'test_')\n\
\n\
class Test%s(xmotoTestCase):\n\
    def setUp(self):\n\
        xmotoTestCase.setUp(self, testDir)\n\
\n\
" % (sessionId, sessionId)

        testTest = "\
    def %s(self):\n\
        test = %s\n\
        self.buildTest(test)\n\
\n\
"

        testFooter = "\
if __name__ == '__main__':\n\
    unittest.main()\n\
\n"

        testFile = join(self.testsDir, 'test_%s.py' % sessionId)
        f = open(testFile, 'wb')

        f.write(testHeader)

        for testId, testValues in tests.items():
            f.write(testTest % (testId, testValues))

        f.write(testFooter)

        f.close()

        self.deleteTests()

    def getTests(self):
        tests = {}
        searchPathname = join(self.testsDir,
                              'test_*.py')
        files = glob.glob(searchPathname)
        for f in files:
            testId = basename(f)[:-len('.py')]
            fh = open(f, 'rb')
            content = fh.read()
            fh.close()

            # the file containts an instruction:
            # test = {'xxx': }
            exec(content)

            if len(test['gtkCmds']) != 0:
                # put the apply/cancel button click at the end
                pos = -1
                try:
                    pos = test['gtkCmds'].index("self.get('apply').clicked()")
                except:
                    try:
                        pos = test['gtkCmds'].index("self.get('cancel').clicked()")
                    except:
                        pass

                if pos != -1:
                    test['gtkCmds'].append(test['gtkCmds'][pos])
                    del test['gtkCmds'][pos]

            tests[testId] = test

        return tests

    def deleteTests(self):
        tests = {}
        searchPathname = join(self.testsDir,
                              'test_[0-9]*.py')
        files = glob.glob(searchPathname)
        for f in files:
            remove(f)

    def addInSvg(self, file):
        # create in svg file
        svgIn = 'in_%d.svg' % self.conf['currentTest']
        svgInFull = join(self.testsDir, 'in', svgIn)
        createDirsOfFile(svgInFull)
        copyfile(file, svgInFull)
        self.testValues['in'] = svgIn

    def addOutSvg(self, doc):
        svgOut = join('out_%d.svg' % self.conf['currentTest'])
        svgOutFull = join(self.testsDir, 'out', svgOut)
        createDirsOfFile(svgOutFull)
        file = open(svgOutFull, 'wb')
        doc.write(file)
        file.close()
        self.testValues['out'] = svgOut

    def addTestArgvModule(self, options, module):
        testArgs = []
        for arg in vars(options):
            value = getattr(options, arg)
            if arg == 'ids':
                for ids in value:
                    testArgs.append('--id=%s' % ids)
            else:
                testArgs.append('--%s=%s' % (arg, value))

        self.testValues['argv'] = testArgs
        self.testValues['module'] = basename(sys.argv[0])[:-len('.py')]

    def addGtkCmd(self, cmd):
        self.testValues['gtkCmds'].append(cmd)

    def writeTestValues(self):
        testOut = join(self.testsDir,
                       'test_%d.py' % self.conf['currentTest'])
        f = open(testOut, 'wb')
        f.write('test = %s' % self.testValues)
        f.close()
