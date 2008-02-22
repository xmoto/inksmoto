from os.path import expanduser, join, isdir
import os

notSetBitmap = ['_None_', '', None, 'None']

def getInkscapeExtensionsDir():
    system = os.name
    if system == 'nt':
        # check this value from a Windows machine
        userDir = expanduser('~/Application Data/Inkscape/extensions')

        # if the userDir exists, use it. else, use the appsDir
        if isdir(userDir):
            return userDir
        else:
            return join(os.getcwd(), "share\\extensions")
    else:
        return expanduser('~/.inkscape/extensions')

def getValue(dictValues, namespace, name=None, default=None):
    try:
        if name is not None:
            value =  dictValues[namespace][name]
        else:
            value = dictValues[namespace]

        if value is None:
            return default
        else:
            return value
    except:
        return default

def createIfAbsent(dict, key):
    if not key in dict:
        dict[key] = {}
            
def delWithoutExcept(dict, value):
    try:
        del dict[value]
    except:
        pass

def alphabeticSortOfKeys(sequence):
    compareFunc = lambda x, y: cmp(x.lower(), y.lower())
    if type(sequence) == dict:
        keys = sequence.keys()
        keys.sort(cmp=compareFunc)
        return keys
    else:
        sequence.sort(cmp=compareFunc)
        return sequence

def setOrDelBool(dict, widget, key):
    if widget.get() == 1:
        dict[key] = 'true'
    else:
        delWithoutExcept(dict, key)

def setOrDelBitmap(dict, key, button):
    bitmapName = button.get()
    if bitmapName not in notSetBitmap:
        dict[key] = bitmapName
    else:
        delWithoutExcept(dict, key)
