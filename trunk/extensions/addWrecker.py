from addEntity import AddEntity

class AddWrecker(AddEntity):
    def __init__(self):
        AddEntity.__init__(self)
        self.typeid = 'Wrecker'
    
if __name__ == "__main__":
    e = AddWrecker()
    e.affect()
