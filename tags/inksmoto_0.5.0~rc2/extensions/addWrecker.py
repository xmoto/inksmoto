from addEntity import AddEntity

class AddWrecker(AddEntity):
    def __init__(self):
        AddEntity.__init__(self)
        self.typeid = 'Wrecker'
    
e = AddWrecker()
e.affect()
