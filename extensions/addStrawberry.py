from addEntity import AddEntity

class AddStrawberry(AddEntity):
    def __init__(self):
        AddEntity.__init__(self)
        self.typeid = 'Strawberry'

e = AddStrawberry()
e.affect()
