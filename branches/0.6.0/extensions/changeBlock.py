from xmotoExtensionTkinter import XmExtTkElement
from xmotoTools import createIfAbsent, delWithoutExcept
import xmGui
from factory import Factory

class ChangeBlock(XmExtTkElement):
    def __init__(self):
        XmExtTkElement.__init__(self)
        self.defGrip  = 20.0
        self.defMass  = 30.0
        self.defElasticity = 0.0
        self.defFriction = 0.5
        self.namespacesInCommon = ['position', 'physics']

    def getUserChanges(self):
        delWithoutExcept(self.commonValues, 'position')
        delWithoutExcept(self.commonValues, 'physics')
        # if the block has been set as an entity
        delWithoutExcept(self.commonValues, 'typeid')

        # handle position
        createIfAbsent(self.commonValues, 'position')
        self.setOrDelBool(self.commonValues, 'position',
                          self.background, 'background')
        self.setOrDelBool(self.commonValues, 'position',
                          self.dynamic, 'dynamic')
        self.setOrDelBool(self.commonValues, 'position',
                          self.physics, 'physics')

        createIfAbsent(self.commonValues, 'physics')
        self.commonValues['physics']['grip'] = self.grip.get()
        if 'physics' in self.commonValues['position']:
            self.setOrDelBool(self.commonValues, 'physics',
                              self.infinity, 'infinitemass')
            self.commonValues['physics']['mass']       = self.mass.get()
            self.commonValues['physics']['elasticity'] = self.elasticity.get()
            self.commonValues['physics']['friction']   = self.friction.get()
        else:
            for var in ['mass', 'elasticity', 'friction']:
                delWithoutExcept(self.commonValues['physics'], var)

        return self.commonValues

    def createWindow(self):
        f = Factory()
        xmGui.defineWindowHeader(title='Block properties')

        # type
        f.createObject('XmTitle', "Type")
        f.createObject('XmLabel', "Uncheck all to convert into normal block.")
        value = self.getValue(self.commonValues, 'position', 'background')
        self.background = f.createObject('XmCheckbox',
                                         value,
                                         text='Background block')
        value = self.getValue(self.commonValues, 'position', 'dynamic')
        self.dynamic = f.createObject('XmCheckbox',
                                      value,
                                      text='Dynamic block')
        value = self.getValue(self.commonValues, 'position', 'physics')
        self.physics = f.createObject('XmCheckbox',
                                      value,
                                      text='Physics block',
                                      command=self.physicsCallback)

        # physic
        f.createObject('XmTitle', "Ode Physic")
        f.createObject('XmLabel', "The grip with the bike wheels")
        value =  self.getValue(self.commonValues, 'physics',
                               'grip', default=self.defGrip)
        self.grip = f.createObject('XmScale',
                                   value,
                                   label='Grip', from_=0, to=50,
                                   resolution=1, default=self.defGrip)

        f.createObject('XmTitle', "Chipmunk Physic")
        value = self.getValue(self.commonValues, 'physics',
                              'infinitemass')
        self.infinity = f.createObject('XmCheckbox',
                                       value,
                                       text='Infinite Mass')
        value = self.getValue(self.commonValues, 'physics',
                              'mass', default=self.defMass)
        self.mass = f.createObject('XmScale',
                                   value,
                                   label='Mass', from_=1, to=1000,
                                   resolution=1, default=self.defMass)
        value = self.getValue(self.commonValues, 'physics',
                              'elasticity', default=self.defElasticity)
        self.elasticity = f.createObject('XmScale',
                                         value,
                                         label='Elasticity', from_=0.0, to=1.0,
                                         resolution=0.1, default=self.defElasticity)
        value = self.getValue(self.commonValues, 'physics',
                              'friction', default=self.defFriction)
        self.friction = f.createObject('XmScale',
                                       value,
                                       label='Friction', from_=0.0, to=1.0,
                                       resolution=0.1, default=self.defFriction)
        self.physicsCallback()

    def physicsCallback(self):
        if self.physics.get() == 1:
            self.infinity.show()
            self.mass.show()
            self.elasticity.show()
            self.friction.show()
        else:
            self.infinity.hide()
            self.mass.hide()
            self.elasticity.hide()
            self.friction.hide()

def run():
    ext = ChangeBlock()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
