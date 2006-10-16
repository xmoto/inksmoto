from factory  import Factory
from stats    import Stats
from elements import Element
import logging, log

class Entity(Element):
    def __init__(self, *args, **keywords):
        Element.__init__(self, *args, **keywords)
        Stats().addEntity(self.id)

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

	# FIXME::to be update with the new dic format
        if self.elementInformations.has_key('size'):
            radius = self.elementInformations['size']
        else:
            radius = self.radius

        self.content.append("\t\t<size r=\"%s\"/>" % str(radius))
        self.content.append("\t\t<position x=\"%f\" y=\"%f\"/>" % self.getEntityPos())
        self.writeEntityParams()
        self.content.append("\t</entity>")
        
        return self.content

    def getEntityPos(self):
        # a path alway begins with 'M posx posy'
        element, valuesDic = self.vertex.pop(0)
        return self.pointInLevelSpace(valuesDic['x'], valuesDic['y'])

    def writeEntityParams(self):
        #<param name="xxx" value="yyy"        
        del self.elementInformations['typeid']
        
        self.content.extend(["\t\t<param name=\"%s\" value=\"%s\"/>" % (key, str(value)) for key, value in self.elementInformations.iteritems()])
        
        if not self.elementInformations.has_key('style'):
            self.content.append("\t\t<param name=\"style\" value=\"default\"/>")


class EndOfLevel(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.5
        self.typeid = 'EndOfLevel'

class Strawberry(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.5
        self.typeid = 'Strawberry'

class PlayerStart(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.4
        self.typeid = 'PlayerStart'

class Sprite(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.4
        self.typeid = 'Sprite'

class Wrecker(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.4
        self.typeid = 'Wrecker'

class ParticleSource(Entity):
    def __init__(self, *args, **keywords):
        Entity.__init__(self, *args, **keywords)
        self.radius = 0.4
        self.typeid = 'ParticleSource'

def initModule():
    Factory().registerObject('EndOfLevel_element',     EndOfLevel)
    Factory().registerObject('Strawberry_element',     Strawberry)
    Factory().registerObject('PlayerStart_element',    PlayerStart)
    Factory().registerObject('Sprite_element',         Sprite)
    Factory().registerObject('Wrecker_element',        Wrecker)
    Factory().registerObject('ParticleSource_element', ParticleSource)

initModule()
