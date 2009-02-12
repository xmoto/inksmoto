import unittest
import sys
import os
import glob
from lxml import etree

# add inksmoto dir in sys.path
extensionsPath = os.path.normpath(os.path.join(os.getcwd(), '..', '..'))
if extensionsPath not in sys.path:
    sys.path = [extensionsPath] + sys.path

# duplicate from inkex
NSS = {
u'sodipodi' :u'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
u'cc'       :u'http://web.resource.org/cc/',
u'svg'      :u'http://www.w3.org/2000/svg',
u'dc'       :u'http://purl.org/dc/elements/1.1/',
u'rdf'      :u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
u'inkscape' :u'http://www.inkscape.org/namespaces/inkscape',
u'xlink'    :u'http://www.w3.org/1999/xlink',
u'xml'      :u'http://www.w3.org/XML/1998/namespace'
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
    if checkNamespace(node1, node1.tag) == True and checkNamespace(node2, node2.tag) == True:
        return True

    if node1.tag != node2.tag:
        print "tag: \ncorrect[%s]\n != \ntotest[%s]\n" % (str(node1.tag), str(node2.tag))
        return False

    # filter out inkscape and sodipodi items
    node1Items = [str(item).replace('\\n', ' ') for item in sorted(node1.items()) if checkNamespace(node1, item[0]) == False]
    node2Items = [str(item).replace('\\n', ' ') for item in sorted(node2.items()) if checkNamespace(node2, item[0]) == False]
    if node1Items != node2Items:
        print "items: \ncorrect[%s]\n != \ntotest[%s]\n" % (str(node1Items), str(node2Items))
        return False

#    if node1.text != node2.text:
#        print "text: \n%s[%s]\n != \n%s[%s]\n" % (str(node1), str(node1.text), str(node2), str(node2.text))
#        return False

    for child1, child2 in zip(sorted(node1.getchildren(), key=lambda k: k.tag), sorted(node2.getchildren(), key=lambda k: k.tag)):
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
        sys.stdout = open('tmp.log', 'w')

    def restoreStdout(self):
        sys.stdout = self.sysStdout
        os.remove('tmp.log')

    def setUp(self):
        self.noStdout()
        # save modules before launching a test to remove the modules
        # loaded by the current test before the next test
        self.sys_modules_keys = sys.modules.keys()

    def tearDown(self):
        # the module with the commands to execute during the test
        removeModule('testcommands')
        # delete modules loaded by the test
        toDelete = []
        for (name, module) in sys.modules.iteritems():
            if name not in self.sys_modules_keys:
                toDelete.append(name)
        for name in toDelete:
            del sys.modules[name]

    def buildTest(self, test):
        from inksmoto import testcommands
        testcommands.testCommands = test['testCommands']

        # add the parameters for the extension
        inSvgFileName = os.path.join('in', test['inSvgFileName'])
        if not os.path.exists(inSvgFileName):
            raise Exception("svg in file [%s] doesnt exist" % str(inSvgFileName))

        # first arg is the name of the script
        sys.argv = [''] + test['argv'] + [inSvgFileName]

        code = 'import ' + test['module']
        exec(code)
        code = 'e = ' + test['module'] + '.run()'
        exec(code)

        self.restoreStdout()

        toTestSvg = e.document
        correctSvg = getSvg(os.path.join('out', test['correctSvgFileName']))

        self.assert_(areSvgsEqual(correctSvg, toTestSvg))


def getAllTestSuites():
    allSuites = []
    # get suites from all the test_*.py files in the
    # inksmoto_unittests directory
    searchPathname = os.path.join(os.getcwd(), 'test_*.py')
    files = glob.glob(searchPathname)
    modules = [os.path.basename(f[:-len('.py')]) for f in files]
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
