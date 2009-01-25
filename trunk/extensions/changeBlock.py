from xmotoExtensionTkinter import XmotoExtTkElement, XmotoScale, XmotoCheckBox
from xmotoTools import createIfAbsent, delWithoutExcept

class ChangeBlock(XmotoExtTkElement):
    def __init__(self):
        XmotoExtTkElement.__init__(self)
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
        self.defineWindowHeader(title='Block properties')

        # type
        self.defineTitle(self.frame, "Type")
        label = "Uncheck all to convert into normal block."
        self.defineLabel(self.frame, label)
        self.background = XmotoCheckBox(self.frame,
                                        self.getValue(self.commonValues,
                                                      'position',
                                                      'background'),
                                        text='Background block')
        self.dynamic = XmotoCheckBox(self.frame,
                                     self.getValue(self.commonValues,
                                                   'position',
                                                   'dynamic'),
                                     text='Dynamic block')
        self.physics = XmotoCheckBox(self.frame,
                                     self.getValue(self.commonValues,
                                                   'position',
                                                   'physics'),
                                     text='Physics block',
                                     command=self.physicsCallback)

        # physic
        self.defineTitle(self.frame, "Ode Physic")
        self.defineLabel(self.frame, "The grip with the bike wheels")
        self.grip = XmotoScale(self.frame,
                               self.getValue(self.commonValues, 'physics',
                                             'grip', default=self.defGrip),
                               label='Grip', from_=0, to=50,
                               resolution=1, default=self.defGrip)

        self.defineTitle(self.frame, "Chipmunk Physic")
        self.infinity = XmotoCheckBox(self.frame,
                                      self.getValue(self.commonValues,
                                                    'physics',
                                                    'infinitemass'),
                                      text='Infinite Mass')
        self.mass = XmotoScale(self.frame,
                               self.getValue(self.commonValues, 'physics',
                                             'mass', default=self.defMass),
                               label='Mass', from_=1, to=1000,
                               resolution=1, default=self.defMass)
        self.elasticity = XmotoScale(self.frame,
                                     self.getValue(self.commonValues,
                                                   'physics',
                                                   'elasticity',
                                                   default=self.defElasticity),
                                     label='Elasticity', from_=0.0, to=1.0,
                                     resolution=0.1, default=self.defElasticity)
        self.friction = XmotoScale(self.frame,
                                   self.getValue(self.commonValues,
                                                 'physics',
                                                 'friction',
                                                 default=self.defFriction),
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
    e = ChangeBlock()
    e.affect()
    return e

if __name__ == "__main__":
    run()
