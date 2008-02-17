from os.path import expanduser, join, isdir
import os

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

