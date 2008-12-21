from addEntity import AddEntity

class AddEndOfLevel(AddEntity):
    def __init__(self):
        AddEntity.__init__(self)
        self.typeid = 'EndOfLevel'

e = AddEndOfLevel()
e.affect()
