from os.path import expanduser, join, isdir, exists, dirname
from inkex   import addNS, NSS
import logging, log
import os, re

notSetBitmap = ['_None_', '', None, 'None']
notSet = ['', None, 'None']

def applyOnElements(root, elements, function):
    for root.id, element in elements.iteritems():
        if element.tag in [addNS('path', 'svg'), addNS('rect', 'svg'), addNS('image', 'svg')]:
            function(element)
        elif element.tag in [addNS('g', 'svg')]:
            # store sprites as sublayer containing a path and an image
            if element.get(addNS('xmoto_label', 'xmoto')) is not None:
                function(element)
            else:
                # get elements in the group
                for subelement in element.xpath('./svg:path|./svg:rect', namespaces=NSS):
                    function(subelement)

def createDirsOfFile(path):
    dirPath = dirname(path)
    if not isdir(dirPath):
        os.makedirs(dirPath)

def addHomeDirInSysPath():
    """
    put the ~/.inkscape/extensions directory at the top of the sys.path
    to include local modified .py files first
    """
    import sys
    homeDir = getHomeDir()
    if homeDir not in sys.path:
        sys.path = [homeDir] + sys.path

def getExistingImageFullPath(imageName):
    path = join(getHomeDir(), 'xmoto_bitmap', imageName)
    if exists(path):
        return path
    path = join(getSystemDir(), 'xmoto_bitmap', imageName)
    if exists(path):
        return path
    return None

def getHomeDir():
    system  = os.name
    userDir = ""
    if system == 'nt':
        # on some Windows (deutsch for example), the Application Data directory has its name translated
        if 'APPDATA' in os.environ:
            userDir = join(os.environ['APPDATA'], 'Inkscape', 'extensions')
        else:
            path = join('~', 'Application Data', 'Inkscape', 'extensions')
            userDir = expanduser(path)
    else:
        path = join('~', '.inkscape', 'extensions')
        userDir = expanduser(path)
    if not isdir(userDir):
        os.mkdir(userDir)
    return userDir

def getSystemDir():
    # get the system dir in the sys.path
    inkscapeSystemDir = ""
    import sys
    import copy
    # a deep copy because we don't want to modify the existing sys.path
    sys_paths = copy.deepcopy(sys.path)
    sys_paths.reverse()
    for sys_path in sys_paths:
        if 'inkscape' in sys_path.lower() and 'extensions' in sys_path.lower():
            inkscapeSystemDir = sys_path
            break

    # if we can't find it (custom install or something like that)
    if inkscapeSystemDir == "":
        system = os.name
        if system == 'nt':
            inkscapeSystemDir = join(os.getcwd(), "share", "extensions")
        elif system == 'mac':
            inkscapeSystemDir = getHomeDir()
        else:
            # test only /usr/share/inkscape and /usr/local/share/inkscape
            commonDirs = ["/usr/share/inkscape", "/usr/local/share/inkscape"]
            for dir in commonDirs:
                if isdir(dir):
                    inkscapeSystemDir = join(dir, "extensions")
            if inkscapeSystemDir == "":
                inkscapeSystemDir = getHomeDir()

    return inkscapeSystemDir

def getBoolValue(dictValues, namespace, name=None, default=False):
    value = getValue(dictValues, namespace, name, default)
    if value == 'true':
        return True
    else:
        return False

def getValue(dictValues, namespace, name=None, default=None):
    try:
        if name is not None:
            value = dictValues[namespace][name]
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
            
def delWithoutExcept(dict, key, namespace=None):
    try:
        if namespace is None:
            del dict[key]
        else:
            del dict[namespace][key]
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
        return True
    else:
        delWithoutExcept(dict, key)
        return False

def setOrDelBitmap(dict, key, button):
    bitmapName = button.get()
    if bitmapName not in notSetBitmap:
        dict[key] = bitmapName
        return True
    else:
        delWithoutExcept(dict, key)
        return False

def checkId(id):
    return re.search("[^0-9a-zA-Z_]+", id) is None
