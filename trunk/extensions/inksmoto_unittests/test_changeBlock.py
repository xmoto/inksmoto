import unittest
import sys
from xmotoTestCase import areSvgsEqual, xmotoTestCase, getSvg

def getTestSuite():
    return unittest.makeSuite(TestChangeBlock, 'test_')

class TestChangeBlock(xmotoTestCase):
    def test_setAsPhysic(self):
        test = {'inSvgFileName': "test_ChangeBlock.svg",
                'correctSvgFileName': "test_ChangeBlock_out.svg",
                'testCommands': ['self.physics.widget.select()', 'self.ok_button.invoke()'],
                'argv': ["--id=physicblock"],
                'module': 'changeBlock'}
        self.buildTest(test)


if __name__ == '__main__':
    unittest.main()