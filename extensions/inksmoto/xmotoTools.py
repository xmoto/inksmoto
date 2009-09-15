#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import log, logging
from os.path import expanduser, join, isdir, exists, dirname, normpath
from inkex import addNS, NSS
import os, re

NOTSET_BITMAP = ['_None_', '', None, 'None']
NOTSET = ['', None, 'None']

def applyOnElements(root, elements, function):
    for root._id, element in elements.iteritems():
        if element.tag in [addNS('g', 'svg')]:
            # store sprites as sublayer containing a path and an image
            if element.get(addNS('xmoto_label', 'xmoto')) is not None:
                function(element)
            else:
                # get elements in the group
                for subelement in element.xpath('./svg:path|./svg:rect',
                                                namespaces=NSS):
                    function(subelement)
        else:
            function(element)

def createDirsOfFile(path):
    dirPath = dirname(path)
    if not isdir(dirPath):
        os.makedirs(dirPath)

def loadFile(name):
    """
    load files from ~/.inkscape/extensions first
    """
    loadedVars = {}
    try:
        homeFile = join(getHomeDir(), name)
        execfile(homeFile, {}, loadedVars)
    except:
        sysFile = join(getSystemDir(), name)
        execfile(sysFile, {}, loadedVars)

    return loadedVars

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
        # on some Windows (deutsch for example), the Application Data
        # directory has its name translated
        if 'APPDATA' in os.environ:
            userDir = join(os.environ['APPDATA'], 'Inkscape',
                           'extensions')
        else:
            path = join('~', 'Application Data', 'Inkscape',
                        'extensions')
            userDir = expanduser(path)
    else:
        path = join('~', '.inkscape', 'extensions')
        userDir = expanduser(path)
    if not isdir(userDir):
        os.makedirs(userDir)
    return userDir

def getSystemDir():
    """ get the system dir in the sys.path """
    sysDir = ""
    import sys
    import copy
    # a deep copy because we don't want to modify the existing sys.path
    sys_paths = copy.deepcopy(sys.path)
    sys_paths.reverse()
    for sys_path in sys_paths:
        if 'inkscape' in sys_path.lower() and 'extensions' in sys_path.lower():
            sysDir = join(sys_path, 'inksmoto')
            break

    # if we can't find it (custom install or something like that)
    if sysDir == "":
        system = os.name
        if system == 'nt':
            sysDir = join(os.getcwd(), 'share', 'extensions', 'inksmoto')
        elif system == 'mac':
            sysDir = getHomeDir()
        else:
            # test only /usr/share/inkscape and /usr/local/share/inkscape
            commonDirs = ['/usr/share/inkscape', '/usr/local/share/inkscape']
            for _dir in commonDirs:
                if isdir(_dir):
                    sysDir = join(_dir, 'extensions', 'inksmoto')
            if sysDir == "":
                sysDir = getHomeDir()

    return sysDir

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
    except Exception:
        return default

def createIfAbsent(dic, key):
    if not key in dic:
        dic[key] = {}
            
def delWithoutExcept(dic, key, namespace=None):
    try:
        if namespace is None:
            del dic[key]
        else:
            del dic[namespace][key]
    except Exception:
        return

def alphabeticSortOfKeys(sequence):
    compareFunc = lambda x, y: cmp(x.lower(), y.lower())
    if type(sequence) == dict:
        keys = sequence.keys()
        keys.sort(cmp=compareFunc)
        return keys
    else:
        sequence.sort(cmp=compareFunc)
        return sequence

def setOrDelBool(dic, key, value, dontDel=False):
    if value == True:
        dic[key] = 'true'
        return True
    else:
        if dontDel == True:
            dic[key] = 'false'
        else:
            delWithoutExcept(dic, key)
        return dontDel

def setOrDelBitmap(dic, key, bitmapName):
    if bitmapName not in NOTSET_BITMAP:
        dic[key] = bitmapName
        return True
    else:
        delWithoutExcept(dic, key)
        return False

def setOrDelColor(dic, prefix, color):
    """ color is a (r, g, b, a) tuple
    """
    default = 255
    (r, g, b, a) = color
    if ( r != default or g != default or b != default or a != default):
        dic[prefix+'_r'] = r
        dic[prefix+'_g'] = g
        dic[prefix+'_b'] = b
        dic[prefix+'_a'] = a
        return True
    else:
        delWithoutExcept(dic, prefix+'_r')
        delWithoutExcept(dic, prefix+'_g')
        delWithoutExcept(dic, prefix+'_b')
        delWithoutExcept(dic, prefix+'_a')
        return False

def setOrDelValue(dic, key, value, default=None):
    if value != default:
        dic[key] = value
        return True
    else:
        delWithoutExcept(dic, key)
        return False

def checkId(_id):
    return re.search("[^0-9a-zA-Z_]+", _id) is None

def dec2hex(d):
    convert = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5',
               6:'6', 7:'7', 8:'8', 9:'9', 10:'a', 11:'b',
               12:'c', 13:'d', 14:'e', 15:'f'}
    return convert[d]

def hex2dec(x):
    convert = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5,
               '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11,
               'c':12, 'd':13, 'e':14, 'f':15}
    return convert[x]

def conv8to16(x):
    return (x << 8) + x

def conv16to8(x):
    return x >> 8

def updateInfos(toUpdate, newValues):
    for key, value in newValues.iteritems():
        if type(value) == dict:
            namespace = key
            for key, value in value.iteritems():
                createIfAbsent(toUpdate, namespace)
                toUpdate[namespace][key] = value
        else:
            toUpdate[key] = value

def color2Hex(r, g, b):
    def composant2Hex(c):
        c1 = c >> 4
        c2 = c % 16
        return dec2hex(c1) + dec2hex(c2)
    return '#' + composant2Hex(r) + composant2Hex(g) + composant2Hex(b)

def getIndexInList(items, item):
    selection = 0
    try:
        selection = items.index(item)
    except:
        pass
    return selection
