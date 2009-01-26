from factory    import Factory
from stats      import Stats
from elements   import Element
from xmotoTools import createIfAbsent, getValue
from listAvailableElements import sprites
from inksmoto_configuration import defaultCollisionRadius
import logging, log

class Entity(Element):
    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        Stats().addEntity(self.id)
        self.radius = defaultCollisionRadius[self.typeid]

    def writeContent(self, options, level):
        """
        - entity:
          * typeid=[PlayerStart|EndOfLevel|Strawberry|Wrecker|ParticleSource|Sprite]
          * size=float_number (the entity colision radius)
          * param_name=param_value
          ** available params are (there's more of them):
             z     (for Sprite)
             name  (for Sprite)
             type  (for ParticleSource)
        """
        self.newWidth = options['width']
        self.newHeight = options['height']
        self.ratio = options['ratio']
        self.level = level

        self.preProcessVertex()
        self.content.append("\t<entity id=\"%s\" typeid=\"%s\">" % (self.id, self.typeid))

        createIfAbsent(self.infos, 'size')

        if not self.infos['size'].has_key('r'):
            self.infos['size']['r'] = self.radius

        createIfAbsent(self.infos, 'position')

        if not self.infos['position'].has_key('x') or not self.infos['position'].has_key('y'):
            x, y = self.getEntityPos()
            self.infos['position']['x'] = str(x)
            self.infos['position']['y'] = str(y)

        createIfAbsent(self.level.options, 'remplacement')
        self.calculateNewDimensions()

        self.addElementParams()
        self.content.append("\t</entity>")

        return self.content

    def calculateNewDimensions(self):
        pass

    def getEntityPos(self):
        # use the center of the aabb
        return self.pointInLevelSpace(self.aabb.cx(), self.aabb.cy())

    def calculateNewDimensionsForRemplacement(self, name):
        if name+'Scale' not in self.level.options['remplacement']:
            return

        scale = float(self.level.options['remplacement'][name+'Scale'])
        if scale == 1.0:
            return

        sprite = getValue(self.level.options, 'remplacement', name, default=name)
        self.setSize(sprite, scale)

    def setSize(self, name, scale):
        self.infos['size']['r'] = self.radius * scale
        if name in sprites and 'width' in sprites[name] and 'height' in sprites[name]:
            self.infos['size']['width']  = float(sprites[name]['width']) * scale
            self.infos['size']['height'] = float(sprites[name]['height']) * scale
        else:
            self.infos['size']['width']  = scale
            self.infos['size']['height'] = scale
        
class EndOfLevel(Entity):
    def __init__(self, *args, **keywords):
        self.typeid = 'EndOfLevel'
        Entity.__init__(self, *args, **keywords)

    def calculateNewDimensions(self):
        self.calculateNewDimensionsForRemplacement('Flower')

class Strawberry(Entity):
    def __init__(self, *args, **keywords):
        self.typeid = 'Strawberry'
        Entity.__init__(self, *args, **keywords)

    def calculateNewDimensions(self):
        self.calculateNewDimensionsForRemplacement('Strawberry')

class PlayerStart(Entity):
    def __init__(self, *args, **keywords):
        self.typeid = 'PlayerStart'
        Entity.__init__(self, *args, **keywords)

class Sprite(Entity):
    def __init__(self, *args, **keywords):
        self.typeid = 'Sprite'
        Entity.__init__(self, *args, **keywords)

    def calculateNewDimensions(self):
        if 'scale' not in self.infos['size']:
            return

        scale = float(self.infos['size']['scale'])
        del self.infos['size']['scale']
        if scale == 1.0:
            return

        if 'param' not in self.infos:
            return
        if 'name' not in self.infos['param']:
            return
        spriteName = self.infos['param']['name']

        self.setSize(spriteName, scale)

class Wrecker(Entity):
    def __init__(self, *args, **keywords):
        self.typeid = 'Wrecker'
        Entity.__init__(self, *args, **keywords)

    def calculateNewDimensions(self):
        self.calculateNewDimensionsForRemplacement('Wrecker')

class ParticleSource(Entity):
    def __init__(self, *args, **keywords):
        self.typeid = 'ParticleSource'
        Entity.__init__(self, *args, **keywords)

class Joint(Entity):
    def __init__(self, *args, **keywords):
        self.typeid = 'Joint'
        Entity.__init__(self, *args, **keywords)

def initModule():
    Factory().registerObject('EndOfLevel_element',     EndOfLevel)
    Factory().registerObject('Strawberry_element',     Strawberry)
    Factory().registerObject('PlayerStart_element',    PlayerStart)
    Factory().registerObject('Sprite_element',         Sprite)
    Factory().registerObject('Wrecker_element',        Wrecker)
    Factory().registerObject('ParticleSource_element', ParticleSource)
    Factory().registerObject('Joint_element',          Joint)

initModule()
