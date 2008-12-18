import unittest
import sys
from xmotoTestCase import areSvgsEqual, xmotoTestCase, getSvg

def getTestSuite():
    return unittest.makeSuite(TestChangeBlock, 'test_')

class TestChangeBlock(xmotoTestCase):
    def test_setAsPhysic(self):
        test = {'inSvgFileName': "test_ChangeBlock.svg",
                'correctSvgFileName': "test_ChangeBlock_out.svg",
                'testCommands': ['self.physics.widget.select()',
                                 'self.ok_button.invoke()'],
                'argv': ["--id=physicblock"],
                'module': 'changeBlock'}
        self.buildTest(test)

    def test_setAsPhysicalBackground(self):
        test = {'inSvgFileName': "test_ChangeBlock.svg",
                'correctSvgFileName': "test_ChangeBlock_out2.svg",
                'testCommands': ['self.physics.widget.select()',
                                 'self.background.widget.select()',
                                 'self.ok_button.invoke()'],
                'argv': ["--id=physicblock"],
                'module': 'changeBlock'}
        self.buildTest(test)

    def test_setAsPhysicalAndChangePhysicsParams(self):
        test = {'inSvgFileName': "test_ChangeBlock.svg",
                'correctSvgFileName': "test_ChangeBlock_out3.svg",
                'testCommands': ['self.physics.widget.select()',
                                 'self.mass.widget.set(500)',
                                 'self.elasticity.widget.set(0.7)',
                                 'self.friction.widget.set(0.0)',
                                 'self.ok_button.invoke()'],
                'argv': ["--id=physicblock"],
                'module': 'changeBlock'}
        self.buildTest(test)

    def test_setAsPhysicalAndChangePhysicsParams2(self):
        test = {'inSvgFileName': "test_ChangeBlock.svg",
                'correctSvgFileName': "test_ChangeBlock_out4.svg",
                'testCommands': ['self.physics.widget.select()',
                                 'self.grip.widget.set(0)',
                                 'self.infinity.widget.select()',
                                 'self.ok_button.invoke()'],
                'argv': ["--id=physicblock"],
                'module': 'changeBlock'}
        self.buildTest(test)


if __name__ == '__main__':
    unittest.main()
