from addEntity import AddEntity

class AddEndOfLevel(AddEntity):
    def __init__(self):
        AddEntity.__init__(self)
        self.typeid = 'EndOfLevel'

if __name__ == '__main__':
    e = AddEndOfLevel()
    e.affect()
