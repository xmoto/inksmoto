from factory    import Factory
from stats      import Stats
from elements   import Element
from xmotoTools import createIfAbsent
from listAvailableElements import sprites
from inksmoto_configuration import defaultCollisionRadius
import logging, log

class Entity(Element):
    def __init__(self, *args, **keywords):
        Element.__init__(self, *args, **keywords)
        Stats().addEntity(self.id)
        self.radius = defaultCollisionRadius[self.typeid]

    def writeContent(self, **keywords):
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
        logging.debug("Entity-%s-::writeContent:: matrix: %s" % (self.typeid, self.transformMatrix))

        self.newWidth  = keywords['newWidth']
        self.newHeight = keywords['newHeight']
        self.ratio     = keywords['ratio']

        self.preProcessVertex()
        self.content.append("\t<entity id=\"%s\" typeid=\"%s\">" % (self.id, self.typeid))

        createIfAbsent(self.elementInformations, 'size')

        if not self.elementInformations['size'].has_key('r'):
            self.elementInformations['size']['r'] = self.radius

        createIfAbsent(self.elementInformations, 'position')

        if not self.elementInformations['position'].has_key('x') or not self.elementInformations['position'].has_key('y'):
            x, y = self.getEntityPos()
            self.elementInformations['position']['x'] = str(x)
            self.elementInformations['position']['y'] = str(y)

        self.level = keywords['level']
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

        if name in self.level.options['remplacement']:
            sprite = self.level.options['remplacement'][name]
        else:
            sprite = name

        self.elementInformations['size']['r'] = self.radius * scale
        if name in sprites:
            if 'width' in sprites[name] and 'height' in sprites[name]:
                self.elementInformations['size']['width']  = float(sprites[name]['width']) * scale
                self.elementInformations['size']['height'] = float(sprites[name]['height']) * scale

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
        if 'scale' not in self.elementInformations['size']:
            return

        scale = float(self.elementInformations['size']['scale'])
        del self.elementInformations['size']['scale']
        if scale == 1.0:
            return

        if 'param' not in self.elementInformations:
            return
        if 'name' not in self.elementInformations['param']:
            return
        spriteName = self.elementInformations['param']['name']

        self.elementInformations['size']['r'] = self.radius * scale
        if spriteName in sprites:
            if 'width' in sprites[spriteName] and 'height' in sprites[spriteName]:
                self.elementInformations['size']['width']  = float(sprites[spriteName]['width']) * scale
                self.elementInformations['size']['height'] = float(sprites[spriteName]['height']) * scale
            else:
                self.elementInformations['size']['width']  = scale
                self.elementInformations['size']['height'] = scale

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
