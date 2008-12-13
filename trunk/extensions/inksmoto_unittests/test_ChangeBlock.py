import unittest
import sys
from xmotoTestCase import areSvgsEqual, xmotoTestCase, getSvg

def getTestSuite():
    return unittest.makeSuite(TestChangeBlock, 'test_')

class TestChangeBlock(xmotoTestCase):
    def test_setAsPhysic(self):
        inSvgFileName  = "./test_ChangeBlock.svg"
        correctSvgFileName = "./test_ChangeBlock_out.svg"

        import testcommands
        testcommands.testCommands = ['self.physics.widget.select()', 'self.ok_button.invoke()']

        # add the parameters for the extension
        sys.argv += ["--id=physicblock", inSvgFileName]

        # importing the module will launch it.
        import changeBlock

        self.restoreStdout()

        toTestSvg = changeBlock.e.document

        correctSvg = getSvg(correctSvgFileName)

        self.assert_(areSvgsEqual(correctSvg, toTestSvg))

if __name__ == '__main__':
    unittest.main()
