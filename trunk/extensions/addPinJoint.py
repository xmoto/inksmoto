from addJoint import AddJoint
import logging, log

class AddPinJoint(AddJoint):
    def __init__(self):
        AddJoint.__init__(self)
        self.jointType = 'pin'

if __name__ == "__main__":
    e = AddPinJoint()
    e.affect()
