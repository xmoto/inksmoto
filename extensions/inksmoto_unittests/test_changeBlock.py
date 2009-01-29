import unittest
from xmotoTestCase import xmotoTestCase

def getTestSuite():
    return unittest.makeSuite(TestChangeBlock, 'test_')

class TestChangeBlock(xmotoTestCase):
    def test_setAsPhysic(self):
        test = {'inSvgFileName': "test_ChangeBlock.svg",
                'correctSvgFileName': "test_ChangeBlock_out.svg",
                'testCommands': ['self.physics.widget.select()',
                                 'xmGui.invokeOk()'],
                'argv': ["--id=physicblock"],
                'module': 'changeBlock'}
        self.buildTest(test)

if __name__ == '__main__':
    unittest.main()
