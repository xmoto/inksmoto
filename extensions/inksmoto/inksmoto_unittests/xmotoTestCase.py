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

import unittest
import sys
import os
from os.path import join, normpath, exists, basename, dirname, expanduser, isdir
import glob
from lxml import etree
from inksmoto.xmotoTools import getHomeDir, getTempDir

# duplicate from inkex
NSS = {
'sodipodi' :'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
'cc'       :'http://web.resource.org/cc/',
'svg'      :'http://www.w3.org/2000/svg',
'dc'       :'http://purl.org/dc/elements/1.1/',
'rdf'      :'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
'inkscape' :'http://www.inkscape.org/namespaces/inkscape',
'xlink'    :'http://www.w3.org/1999/xlink',
'xml'      :'http://www.w3.org/XML/1998/namespace'
}

# duplicate from svgnode so that we don't have to import svgnode and
# all its prerequisites
def checkNamespace(node, attrib):
    pos1 = attrib.find('{')
    pos2 = attrib.find('}')
    if pos1 != -1 and pos2 != -1:
        namespace = attrib[pos1+1:pos2]
        if namespace in [NSS['inkscape'], NSS['sodipodi']]:
            return True
        # do not test images content
        if namespace == NSS['xlink']:
            tag = attrib[pos2+1:]
            if tag == 'href':
                return True
    return False

def getSystemDir():
    """ special version for tests """
    import sys
    return join(sys.path[0], 'inksmoto')


def getSvg(svgFileName):
    stream = open(svgFileName, 'r')
    svg = etree.parse(stream)
    stream.close()
    return svg

# compare two svgs. we can't test 'tostring' representation of both
# svgs as their attributes can be in different order.
def areSvgsEqual(document1, document2):
    return areElementsEqual(document1.getroot(), document2.getroot())

def areElementsEqual(node1, node2):
    # check that the nodes are not inkscape or sodipodi ones
    if (checkNamespace(node1, node1.tag) == True
        and checkNamespace(node2, node2.tag) == True):
        return True

    if node1.tag != node2.tag:
        print("tag: \ncorrect[%s]\n != \ntotest[%s]\n" % (str(node1.tag),
                                                          str(node2.tag)))
        return False

    # filter out inkscape and sodipodi items
    node1Items = [str(item).replace('\\n', ' ')
                  for item in sorted(node1.items())
                  if checkNamespace(node1, item[0]) == False]
    node2Items = [str(item).replace('\\n', ' ')
                  for item in sorted(node2.items())
                  if checkNamespace(node2, item[0]) == False]
    if node1Items != node2Items:
        print("items: \ncorrect[%s]\n != \ntotest[%s]\n" % (str(node1Items),
                                                            str(node2Items)))
        return False

#    if node1.text != node2.text:
#        print "text: \n%s[%s]\n != \n%s[%s]\n" % (str(node1), str(node1.text),
#                                                  str(node2), str(node2.text))
#        return False

    for child1, child2 in zip(sorted(node1.getchildren(), key=lambda k: k.tag),
                              sorted(node2.getchildren(), key=lambda k: k.tag)):
        if areElementsEqual(child1, child2) == False:
            return False

    return True

def removeModule(module):
    if module in sys.modules:
        del sys.modules[module]

class xmotoTestCase(unittest.TestCase):
    def noStdout(self):
        # do not pollute test out with result svgs
        self.sysStdout = sys.stdout
        sys.stdout = open(join(getTempDir(), 'inksmoto-tests.log'), 'w')

    def restoreStdout(self):
        sys.stdout = self.sysStdout
        os.remove(join(getTempDir(), 'inksmoto-tests.log'))

    def setUp(self, testDir):
        self.noStdout()
        self.oldCwd = os.getcwd()
        os.chdir(testDir)

    def tearDown(self):
        # the module with the commands to execute during the test
        removeModule('testcommands')
        os.chdir(self.oldCwd)

    def buildTest(self, test):
        from inksmoto import testcommands
        testcommands.testCommands = test['gtkCmds']

        # add the parameters for the extension
        inSvgFileName = join('in', test['in'])
        if not exists(inSvgFileName):
            raise Exception("svg in file [%s] doesnt exist" % str(inSvgFileName))

        # first arg is the name of the script
        sys.argv = [''] + test['argv'] + [inSvgFileName]

        code = 'import ' + test['module']
        exec(code)
        code = 'e = ' + test['module'] + '.run()'
        exec(code)

        self.restoreStdout()

        toTestSvg = e.document
        correctSvg = getSvg(join('out', test['out']))

        self.assertTrue(areSvgsEqual(correctSvg, toTestSvg))


def getAllTestSuites():
    # add inksmoto dir in sys.path
    extensionsPath = normpath(join(os.getcwd(), '..', '..'))
    if extensionsPath not in sys.path:
        sys.path = [extensionsPath] + sys.path

    allSuites = []
    # get suites from all the test_*.py files in the
    # inksmoto_unittests directory
    homeTestsDir = join(getHomeDir(), 'cur_tests', '*')
    sysTestsDir = join(getSystemDir(), 'inksmoto_unittests', 'cur_tests', '*')

    for baseDir in [sysTestsDir, homeTestsDir]:
        searchPathname = join(baseDir, 'test_*.py')
        files = glob.glob(searchPathname)

        modules = [(dirname(f), basename(f[:-len('.py')])) for f in files]
        for directory, module in modules:
            try:
                oldDir = os.getcwd()
                os.chdir(directory)
                sys.path = [directory] + sys.path

                code = 'import ' + module
                exec(code)

                code = '%s.testDir = "%s"' % (module, directory)
                exec(code)

                try:
                    code = 'allSuites.append(' + module + '.getTestSuite()' + ')'
                    exec(code)
                except Exception as e:
                    print("ERROR::cant load tests from module '%s'\n\
  error=%s" % (module, e))
                else:
                    print("tests from module '%s' loaded" % module)

                sys.path = sys.path[1:]
                os.chdir(oldDir)

            except Exception as e:
                print("ERROR::cant import module '%s'\n\
  error=%s\n\
  cwd=%s" % (module, e, os.getcwd()))

    return unittest.TestSuite(tuple(allSuites))

def runSuites(suites):
    runner = unittest.TextTestRunner()
    runner.run(suites)

if __name__ == '__main__':
    suites = getAllTestSuites()

    # remove current dir which contains 'inkscape' in it causing
    # getSystemInkscapeExtensionsDir to return the wrong directory
    if os.getcwd() in sys.path:
        sys.path.remove(os.getcwd())

    runSuites(suites)
