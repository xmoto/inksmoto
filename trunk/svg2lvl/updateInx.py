from xml.dom.minidom import Document
from listAvailableElements import textures, edgeTextures, sprites
from listAvailableElements import particleSources, skies, rversions

def createInxHead(nameValue, id, dependencies, params):
    """ create the header of the inx file

    create the name, id, dependencies and params.    
    """
    doc = Document()

    racine = doc.createElement('inkscape-extension')
    doc.appendChild(racine)

    # add the name of the extension
    name = doc.createElement('name')
    nameText = doc.createTextNode(nameValue)
    name.appendChild(nameText)
    racine.appendChild(name)

    # add its id
    idNode = doc.createElement('id')
    idText = doc.createTextNode(id)
    idNode.appendChild(idText)
    racine.appendChild(idNode)

    # add its dependencies, which are of two types:
    #  executables
    #  extension
    for typeDep, text in dependencies:
        dependency = doc.createElement('dependency')
        dependency.setAttribute('type', typeDep)
        dependency.setAttribute('location', 'extensions')
        dependencyText = doc.createTextNode(text)
        dependency.appendChild(dependencyText)
        racine.appendChild(dependency)

    # add its attributes.
    for attributes, text in params:
        paramNode = doc.createElement('param')
        for name, value in attributes:
            paramNode.setAttribute(name, value)

        if type(text) == dict:
            for itemValue in text.keys():
                item     = doc.createElement('item')
                itemText = doc.createTextNode('%s' % itemValue)
                item.appendChild(itemText)
                paramNode.appendChild(item)
        elif type(text) == list:
            for itemValue in text:
                item     = doc.createElement('item')
                itemText = doc.createTextNode('%s' % itemValue)
                item.appendChild(itemText)
                paramNode.appendChild(item)
        else:
            paramText = doc.createTextNode(str(text))
            paramNode.appendChild(paramText)
        racine.appendChild(paramNode)

    return (doc, racine)

def createInxFoot(doc, racine, commandValue, file):
    script = doc.createElement('script')
    command = doc.createElement('command')
    command.setAttribute('reldir', 'extensions')
    command.setAttribute('interpreter', 'python')
    commandText = doc.createTextNode(commandValue)
    command.appendChild(commandText)
    script.appendChild(command)
    racine.appendChild(script)

    f = open(file, 'w')
    f.write(doc.toxml())
    f.close()
    
def updateOutputInxFile(**kwargs):
    nameValue = kwargs['nameValue']
    id = kwargs['id']
    dependencies = kwargs['dependencies']
    params = kwargs['params']
    commandValue = kwargs['commandValue']
    file = kwargs['file']

    extensionText = kwargs['extensionText']
    mimeTypeText  = kwargs['mimeTypeText']
    _fileTypeNameText = kwargs['_fileTypeNameText']
    _fileTypeTooltip  = kwargs['_fileTypeTooltip']

    (doc, racine) = createInxHead(nameValue, id, dependencies, params)

    output = doc.createElement('output')

    for name, text in [('extension',        extensionText),
                       ('mimetype',         mimeTypeText),
                       ('_filetypename',    _fileTypeNameText),
                       ('_filetypetooltip', _fileTypeTooltip),
                       ('dataloss',         'TRUE')]:
        node = doc.createElement(name)
        textNode = doc.createTextNode(text)
        node.appendChild(textNode)
        output.appendChild(node)

    racine.appendChild(output)

    createInxFoot(doc, racine, commandValue, file)

def updateEffectInxFile(**kwargs):
    nameValue = kwargs['nameValue']
    id = kwargs['id']
    dependencies = kwargs['dependencies']
    params = kwargs['params']
    commandValue = kwargs['commandValue']
    file = kwargs['file']

    subsubmenuText = kwargs['subsubmenuText']

    (doc, racine) = createInxHead(nameValue, id, dependencies, params)

    effect = doc.createElement('effect')

    object_type = doc.createElement('object-type')
    object_typeText = doc.createTextNode('path')
    object_type.appendChild(object_typeText)
    effect.appendChild(object_type)

    effects_menu = doc.createElement('effects-menu')
    effect.appendChild(effects_menu)

    submenu = doc.createElement('submenu')
    submenu.setAttribute('_name', 'X-moto')
    effects_menu.appendChild(submenu)

    subsubmenu = doc.createElement('submenu')
    subsubmenu.setAttribute('_name', subsubmenuText)
    submenu.appendChild(subsubmenu)

    racine.appendChild(effect)

    createInxFoot(doc, racine, commandValue, file)

def updateChangeBlockTexture_inx():
    updateEffectInxFile(nameValue      = 'Change Block Texture',
                        id             = 'org.ekips.filter.changeblocktexture',
                        dependencies   = [('executable', 'changeBlockTexture.py'),
                                        ('executable', 'inkex.py')],
                        params         = [([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue   = 'changeBlockTexture.py',
                        file           = './changeBlockTexture.inx',
                        subsubmenuText = 'Blocks')

def updateAddEdge_inx():
    updateEffectInxFile(nameValue      = 'Add an edge around the block',
                        id             = 'org.ekips.filter.addedge',
                        dependencies   = [('executable', 'addEdge.py'),
                                          ('executable', 'inkex.py')],
                        params         = [([['name', 'texture'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'Edge texture']],
                                           edgeTextures)],
                        commandValue   = 'addEdge.py',
                        file           = './addEdge.inx',
                        subsubmenuText = 'Blocks')


def updateAddBackgroundBlock_inx():
    updateEffectInxFile(nameValue    = 'Convert into Background Block',
                        id           = 'org.ekips.filter.addbackgroundblock',
                        dependencies = [('executable', 'addBackgroundBlock.py'),
                                        ('executable', 'inkex.py')],
                        params       = [([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue = 'addBackgroundBlock.py',
                        file         = './addBackgroundBlock.inx',
                        subsubmenuText = 'Blocks')

def updateAddDynamicBlock_inx():
    updateEffectInxFile(nameValue    = 'Convert into Dynamic Block',
                        id           = 'org.ekips.filter.adddynamicblock',
                        dependencies = [('executable', 'addDynamicBlock.py'),
                                        ('executable', 'inkex.py')],
                        params       = [([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue = 'addDynamicBlock.py',
                        file         = './addDynamicBlock.inx',
                        subsubmenuText = 'Blocks')

def updateAddNormalBlock_inx():
    updateEffectInxFile(nameValue    = 'Convert into Normal Block',
                        id           = 'org.ekips.filter.addnormalblock',
                        dependencies = [('executable', 'addNormalBlock.py'),
                                        ('executable', 'inkex.py')],
                        params       = [([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue = 'addNormalBlock.py',
                        file         = './addNormalBlock.inx',
                        subsubmenuText = 'Blocks')

def updateAddSprite_inx():
    updateEffectInxFile(nameValue      = 'Convert into Sprite',
                        id             = 'org.ekips.filter.addsprite',
                        dependencies   = [('executable', 'addSprite.py'),
                                          ('executable', 'inkex.py')],
                        params         = [([['name', 'name'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'Sprite name']],
                                           sprites),
                                          ([['name', 'z'],
                                            ['type', 'int'],
                                            ['min', '-1'],
                                            ['max', '1'],
                                            ['_gui-text', 'Sprite z']],
                                           '-1')],
                        commandValue   = 'addSprite.py',
                        file           = './addSprite.inx',
                        subsubmenuText = 'Entities')

def updateAddParticleSource_inx():
    updateEffectInxFile(nameValue      = 'Convert into Particle Source',
                        id             = 'org.ekips.filter.addparticlesource',
                        dependencies   = [('executable', 'addParticleSource.py'),
                                          ('executable', 'inkex.py')],
                        params         = [([['name', 'type'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'Particle source type']],
                                           particleSources)],
                        commandValue   = 'addParticleSource.py',
                        file           = './addParticleSource.inx',
                        subsubmenuText = 'Entities')

def updateSvg2lvl_inx():
    updateOutputInxFile(nameValue      = 'Xmoto - svg2lvl',
                        id             = 'org.inkscape.output.lvl',
                        dependencies   = [('extension', 'org.inkscape.output.svg.inkscape'),
                                          ('executable', 'svg2lvl.py')],
                        params         = [([['name', 'smooth'],
                                            ['type', 'float'],
                                            ['min',  '0.0'],
                                            ['max',  '100.0'],
                                            ['_gui-text', 'smoothitude']],
                                           '95.0'),
                                          ([['name', 'lua'],
                                            ['type', 'string'],
                                            ['_gui-text', 'lua script']],
                                           'None'),
                                          ([['name', 'id'],
                                            ['type', 'string'],
                                            ['_gui-text', 'level id']],
                                           'noname'),
                                          ([['name', 'name'],
                                            ['type', 'string'],
                                            ['_gui-text', 'level name']],
                                           'Unnamed Level'),
                                          ([['name', 'author'],
                                            ['type', 'string'],
                                            ['_gui-text', 'author']],
                                           'Me'),
                                          ([['name', 'desc'],
                                            ['type', 'string'],
                                            ['_gui-text', 'description']],
                                           'My description'),
                                          ([['name', 'sky'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'sky']],
                                           skies),
                                          ([['name', 'rversion'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'required xmoto version']],
                                           rversions)],
                        commandValue   = 'svg2lvl.py',
                        file           = 'svg2lvl.inx',
                        extensionText  = '.lvl',
                        mimeTypeText   = 'lvl/X-Moto Level',
                        _fileTypeNameText = 'X-Moto Level (*.lvl)',
                        _fileTypeTooltip  = 'X-Moto Level')

def updateInx():
    updateChangeBlockTexture_inx()
    updateAddEdge_inx()
    updateAddSprite_inx()
    updateAddParticleSource_inx()
    updateSvg2lvl_inx()
    updateAddBackgroundBlock_inx()
    updateAddDynamicBlock_inx()
