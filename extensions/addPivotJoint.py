from addJoint import AddJoint
import logging, log

class AddPivotJoint(AddJoint):
    def __init__(self):
        AddJoint.__init__(self)
        self.jointType = 'pivot'

if __name__ == "__main__":
    e = AddPivotJoint()
    e.affect()
