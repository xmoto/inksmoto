from inksmoto.addJoint import AddJoint

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddJoint('pivot')
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
