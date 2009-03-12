from os.path import expanduser, join, isdir, exists, dirname
import logging, log
import os, re
from inkex import addNS, NSS

notSetBitmap = ['_None_', '', None, 'None']

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
    homeDir = getHomeInkscapeExtensionsDir()
    if homeDir not in sys.path:
        sys.path = [homeDir] + sys.path

def getExistingImageFullPath(imageName):
    path = join(getHomeInkscapeExtensionsDir(), 'xmoto_bitmap', imageName)
    if exists(path):
        return path
    path = join(getSystemInkscapeExtensionsDir(), 'xmoto_bitmap', imageName)
    if exists(path):
        return path
    return None

def getHomeInkscapeExtensionsDir():
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
        os.makedirs(userDir)
    return userDir

def getSystemInkscapeExtensionsDir():
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
            inkscapeSystemDir = getHomeInkscapeExtensionsDir()
        else:
            # test only /usr/share/inkscape and /usr/local/share/inkscape
            commonDirs = ["/usr/share/inkscape", "/usr/local/share/inkscape"]
            for dir in commonDirs:
                if isdir(dir):
                    inkscapeSystemDir = join(dir, "extensions")
            if inkscapeSystemDir == "":
                inkscapeSystemDir = getHomeInkscapeExtensionsDir()

    return inkscapeSystemDir

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

def checkLevelId(id):
    return re.search("[^0-9a-zA-Z_]+", id) is None

def dec2hex(d):
    convert = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'a', 11:'b', 12:'c', 13:'d', 14:'e', 15:'f'}
    return convert[d]

def hex2dec(x):
    convert = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
    return convert[x]

def updateLayerInfos(document, layersInfos):
    """ when an user updates the svg ordering in inkscape, he has
    to open the layers properties window in order to the layers
    infos in the metadatas to be updated.  put this updates into
    this function so that it can be called from the .lvl creation
    code and from the layerinfos window
    """
    def extractIndexFromKey(key):
        return int(key[len('layer_'):-len('_id')])

    # metadata layerId -> layerIndex
    oldLayersIdToIndex = {}
    maxLayerIndex = -1
    for (key, layerId) in layersInfos.iteritems():
        if key[-3:] != '_id':
            continue
        layerIndex = extractIndexFromKey(key)
        if layerIndex > maxLayerIndex:
            maxLayerIndex = layerIndex
        oldLayersIdToIndex[layerId] = layerIndex

    # svg layers
    layers = document.xpath('/svg:svg/svg:g', namespaces=NSS)
    nblayers = len(layers)

    # svg layerId -> layerLabel
    layersLabel = []
    for layer in layers:
        layerId = layer.get('id')
        layerLabel = layer.get(addNS('label', 'inkscape'), '')
        layersLabel.append((layerId, layerLabel))

    # existing layers in the right order
    layersIdToIndexToSave = []
    for layerIndex in reversed(xrange(nblayers)):
        # get old layer index or create a new one if it's a new layer
        layerLabel = layersLabel[layerIndex][1]
        if layerLabel == "":
            layerLabel = '#' + layerId

        layerId = layersLabel[layerIndex][0]
        if layerId in oldLayersIdToIndex:
            oldLayerIndex = oldLayersIdToIndex[layerId]
        else:
            maxLayerIndex += 1
            oldLayerIndex = maxLayerIndex
            oldLayersIdToIndex[layerId] = oldLayerIndex

        # keep only layers who are still there. reorder them in
        # the metadata in the same order as in the svg
        layersIdToIndexToSave.append((layerId, layerLabel,
                                      layerIndex, oldLayerIndex))

    # keep only the still existing layers
    layers = {}
    numberMainLayers = 0
    for (layerId,
         layerLabel,
         layerIndex,
         oldLayerIndex) in layersIdToIndexToSave:
        prefix = 'layer_%d_' % layerIndex
        prefixOld = 'layer_%d_' % oldLayerIndex
        layers[prefix+'id'] = layerId

        value = getValue(layersInfos, prefixOld+'isused', default='true')
        layers[prefix+'isused'] = value

        value = getValue(layersInfos, prefixOld+'ismain', default='false')
        layers[prefix+'ismain'] = value

        value = getValue(layersInfos, prefixOld+'x', default=1.0)
        layers[prefix+'x'] = value

        value = getValue(layersInfos, prefixOld+'y', default=1.0)
        layers[prefix+'y'] = value

    return (layers, layersIdToIndexToSave)
