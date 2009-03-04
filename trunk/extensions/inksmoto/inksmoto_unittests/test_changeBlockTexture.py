import unittest
import os
from xmotoTestCase import xmotoTestCase, getSystemDir

def getTestSuite():
    return unittest.makeSuite(TestChangeBlockTexture, 'test_')

class TestChangeBlockTexture(xmotoTestCase):
    def setUp(self):
        xmotoTestCase.setUp(self)
        os.chdir(os.path.join(getSystemDir(), 'inksmoto_unittests'))

    def test_setTextureSand(self):
        test = {'in': "test_ChangeBlockTexture.svg",
                'out': "test_ChangeBlockTexture_out.svg",
                'tkCmds': ["self.updateBitmap('Sand', 'texture')",
                           'xmGui.invokeOk()'],
                'argv': ["--id=block1"],
                'module': 'changeBlockTexture'}
        self.buildTest(test)

if __name__ == '__main__':
    unittest.main()
