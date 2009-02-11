from inksmoto.addEntity import AddEntity

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddEntity('Wrecker')
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
