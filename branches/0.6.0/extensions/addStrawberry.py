from addEntity import AddEntity

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddEntity('Strawberry')
    ext.affect()
    return ext

if __name__ == '__main__':
    run()