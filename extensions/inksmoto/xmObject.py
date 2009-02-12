from parsers import LabelParser, StyleParser
from factory import Factory

class xmIn:
    def __init__(self, node):
        self.node = node

    def getLabel(self):
        pass

class xmOut:
    def __init__(self, node):
        self.node = node

    def update(self, label):
        pass


class xmObject(type):
    def __init__(self, in_, out):
        self.in_ = in_
        self.out = out

class xmEntity(xmObject):
    pass

class xmPlayerStart(xmEntity):
    pass

class xmEndOfLevel(xmEntity):
    pass

class xmParticleSource(xmEntity):
    pass

class xmSprite(xmEntity):
    pass

class xmStrawberry(xmEntity):
    def __init__(self, ):
        xmEntity.__init__(self, )

class xmWrecker(xmEntity):
    pass

class xmZone(xmEntity):
    pass

class xmJoint(xmEntity):
    pass

class xmBlock(xmObject):
    pass


class xmObjectsFactory(Factory):
    def __init__(self):
        pass

    def createFromXmIn(self, in_, out):
        """ 
            -no xm_label on the node: xmNone
            -xm_label but no typeid in it: xmBlock
            -xm_label and typeid: xmEntity
        """
        label = in_.getLabel()

        if label != {} and 'typeid' in label:
            name = label['typeid']
        else:
            name = 'Block'

        if name in self.objects:
            return self.objects[name](in_, out)
        else:
            raise Exception("Object %s not registered in the factory" % name)

def initModule():
    xmObjectsFactory().registerObject('PlayerStart', xmPlayerStart)
    xmObjectsFactory().registerObject('EndOfLevel', xmEndOfLevel)
    xmObjectsFactory().registerObject('ParticleSource', xmParticleSource)
    xmObjectsFactory().registerObject('Sprite', xmSprite)
    xmObjectsFactory().registerObject('Strawberry', xmStrawberry)
    xmObjectsFactory().registerObject('Wrecker', xmWrecker)
    xmObjectsFactory().registerObject('Zone', xmZone)
    xmObjectsFactory().registerObject('Joint', xmJoint)
    xmObjectsFactory().registerObject('Block', xmBlock)

initModule()
