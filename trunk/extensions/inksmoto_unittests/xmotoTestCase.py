import unittest
import sys
import os
import glob
from lxml import etree


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
    if node1.tag != node2.tag:
        print "tag: \n[%s]\n != \n[%s]\n" % (node1.tag, node2.tag)
        return False
    if sorted(node1.items()) != sorted(node2.items()):
        print "items: \n[%s]\n != \n[%s]\n" % (sorted(node1.items()), sorted(node2.items()))
        return False
    if node1.text != node2.text:
        print "text: \n[%s]\n != \n[%s]\n" % (str(node1.text), str(node2.text))
        return False
    for child1, child2 in zip(sorted(node1.getchildren(), key=lambda k: k.tag), sorted(node2.getchildren(), key=lambda k: k.tag)):
        return areElementsEqual(child1, child2)
    return True


class xmotoTestCase(unittest.TestCase):
    def noStdout(self):
        # do not pollute test out with result svgs
        self.sysStdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')

    def restoreStdout(self):
        sys.stdout = self.sysStdout

    def setUp(self):
        self.noStdout()

    def buildTest(self, test):
        import testcommands
        testcommands.testCommands = test['testCommands']

        # add the parameters for the extension
        sys.argv += test['argv'] + [test['inSvgFileName']]

        # importing the module will launch it.
        code = 'import ' + test['module']
        exec(code)

        self.restoreStdout()

        code = 'toTestSvg = ' + test['module'] + '.e.document'
        exec(code)

        correctSvg = getSvg(test['correctSvgFileName'])

        self.assert_(areSvgsEqual(correctSvg, toTestSvg))

def getAllTestSuites():
    allSuites = []
    # get suites from all the test_*.py files in the
    # inksmoto_unittests directory
    searchPathname = os.path.join(os.getcwd(), 'test_*.py')
    files = glob.glob(searchPathname)
    modules = [os.path.basename(f[:-3]) for f in files]
    for module in modules:
        try:
            code = 'import ' + module
            exec(code)

            try:
                code = 'allSuites.append(' + module + '.getTestSuite()' + ')'
                exec(code)
            except:
                print "ERROR::cant load tests from module '%s'" % module
            else:
                print "tests from module '%s' loaded" % module

        except:
            print "ERROR::cant import module '%s'" % module

    print "\navailable test suites are %s\n" % str(allSuites)

    return unittest.TestSuite(tuple(allSuites))

def runSuites(suites):
    runner = unittest.TextTestRunner()
    runner.run(suites)


if __name__ == '__main__':
    # add inksmoto dir in sys.path
    extensionsPath = os.path.normpath(os.path.join(os.getcwd(), '..'))
    if extensionsPath not in sys.path:
        sys.path = [extensionsPath] + sys.path

    suites = getAllTestSuites()

    # remove current dir which contains 'inkscape' in it causing
    # getSystemInkscapeExtensionsDir to return the wrong directory
    if os.getcwd() in sys.path:
        sys.path.remove(os.getcwd())

    runSuites(suites)
