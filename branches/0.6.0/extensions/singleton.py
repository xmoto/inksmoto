# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/412551

class Singleton(type):
    def __init__(mcs, *args):
        type.__init__(mcs, *args)
        mcs._instances = {}

    def __call__(mcs, *args):
        if not args in mcs._instances:
            mcs._instances[args] = type.__call__(mcs, *args)
        return mcs._instances[args]

# exemple usage:
#class Test:
#    __metaclass__=Singleton
#    def __init__(self, *args):
#        pass
