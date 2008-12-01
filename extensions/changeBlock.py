from xmotoExtensionTkinter import XmotoExtTkElement, XmotoListbox, XmotoScale, XmotoEntry, XmotoLabel, XmotoCheckBox
from xmotoTools import getValue, createIfAbsent, delWithoutExcept, setOrDelBool
from listAvailableElements import textures, edgeTextures
import Tkinter

class ChangeBlock(XmotoExtTkElement):
    def __init__(self):
        XmotoExtTkElement.__init__(self)
        self.defaultGrip  = 20.0
        self.defaultMass  = 30.0
        self.defaultElasticity = 0.0
        self.defaultFriction = 0.5

    def getUserChanges(self):
        delWithoutExcept(self.commonValues, 'position')
        delWithoutExcept(self.commonValues, 'physics')

        # handle position
        createIfAbsent(self.commonValues, 'position')
        setOrDelBool(self.commonValues['position'], self.background, 'background')
        setOrDelBool(self.commonValues['position'], self.dynamic,    'dynamic')
        setOrDelBool(self.commonValues['position'], self.physics,    'physics')

        createIfAbsent(self.commonValues, 'physics')
        self.commonValues['physics']['grip'] = self.grip.get()
        if 'physics' in self.commonValues['position']:
            setOrDelBool(self.commonValues['physics'], self.infinity, 'infinitemass')
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
        self.defineLabel(self.frame, "Uncheck all to convert into normal block.")
        self.background = XmotoCheckBox(self.frame, getValue(self.commonValues, 'position', 'background'), text='Background block')
        self.dynamic    = XmotoCheckBox(self.frame, getValue(self.commonValues, 'position', 'dynamic'),    text='Dynamic block')
        self.physics    = XmotoCheckBox(self.frame, getValue(self.commonValues, 'position', 'physics'),    text='Physics block', command=self.physicsCallback)

        # physic
        self.defineTitle(self.frame, "Ode Physic")
        self.defineLabel(self.frame, "The grip with the bike wheels")
        self.grip = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'grip', default=self.defaultGrip), label='Grip', from_=0, to=50, resolution=1, default=self.defaultGrip)

        self.defineTitle(self.frame, "Chipmunk Physic")
        self.infinity = XmotoCheckBox(self.frame, getValue(self.commonValues, 'physics', 'infinitemass'), text='Infinite Mass')
        self.mass = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'mass', default=self.defaultMass), label='Mass', from_=1, to=1000, resolution=1, default=self.defaultMass)
        self.elasticity = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'elasticity', default=self.defaultElasticity), label='Elasticity', from_=0.0, to=1.0, resolution=0.1, default=self.defaultElasticity)
        self.friction = XmotoScale(self.frame, getValue(self.commonValues, 'physics', 'friction', default=self.defaultFriction), label='Friction', from_=0.0, to=1.0, resolution=0.1, default=self.defaultFriction)
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

e = ChangeBlock()
e.affect()
