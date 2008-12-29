from addEntity import AddEntity

class AddPlayerStart(AddEntity):
    def __init__(self):
        AddEntity.__init__(self)
        self.typeid = 'PlayerStart'

if __name__ == "__main__":
    e = AddPlayerStart()
    e.affect()
