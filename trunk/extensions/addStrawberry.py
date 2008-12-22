from addEntity import AddEntity

class AddStrawberry(AddEntity):
    def __init__(self):
        AddEntity.__init__(self)
        self.typeid = 'Strawberry'

if __name__ == "__main__":
    e = AddStrawberry()
    e.affect()
