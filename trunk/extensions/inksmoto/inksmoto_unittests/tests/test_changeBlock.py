import unittest
import os
from xmotoTestCase import xmotoTestCase, getSystemDir

def getTestSuite():
    return unittest.makeSuite(TestChangeBlock, 'test_')

class TestChangeBlock(xmotoTestCase):
    def setUp(self):
        xmotoTestCase.setUp(self)
        os.chdir(os.path.join(getSystemDir(), 'inksmoto_unittests', 'tests'))

    def test_setAsPhysic(self):
        test = {'in': "test_ChangeBlock.svg",
                'out': "test_ChangeBlock_out.svg",
                'tkCmds': ['self.physics.widget.select()',
                           'xmGui.invokeOk()'],
                'argv': ["--id=physicblock"],
                'module': 'changeBlock'}
        self.buildTest(test)

if __name__ == '__main__':
    unittest.main()
