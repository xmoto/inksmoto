import unittest
from xmotoTestCase import xmotoTestCase

def getTestSuite():
    return unittest.makeSuite(TestChangeBlockTexture, 'test_')

class TestChangeBlockTexture(xmotoTestCase):
    def test_setTextureSand(self):
        test = {'inSvgFileName': "test_ChangeBlockTexture.svg",
                'correctSvgFileName': "test_ChangeBlockTexture_out.svg",
                'testCommands': ['self.updateBitmap(\'Sand\', \'texture\')',
                                 'xmGui.invokeOk()'],
                'argv': ["--id=block1"],
                'module': 'changeBlockTexture'}
        self.buildTest(test)

if __name__ == '__main__':
    unittest.main()
