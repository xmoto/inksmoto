from xml.dom.minidom import Document
import logging, log

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

def updateChangeBlockTexture_inx(directory, textures):
    updateEffectInxFile(nameValue      = 'Change Block Texture',
                        id             = 'org.ekips.filter.changeblocktexture',
                        dependencies   = [('executable', 'changeBlockTexture.py'),
                                        ('executable', 'inkex.py')],
                        params         = [([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue   = 'changeBlockTexture.py',
                        file           = directory + '/changeBlockTexture.inx',
                        subsubmenuText = 'Blocks')

def updateAddEdge_inx(directory, edgeTextures):
    updateEffectInxFile(nameValue      = 'Add an edge around the block',
                        id             = 'org.ekips.filter.addedge',
                        dependencies   = [('executable', 'addEdge.py'),
                                          ('executable', 'inkex.py')],
                        params         = [([['name', 'edge_description'],
                                            ['type', 'description']],
                                           "There can be up to two different edge textures for a block. One for the upper side of the block, and another for the down side of the block."),
                                          ([['name', 'update_upper'],
                                            ['type', 'boolean'],
                                            ['_gui-text', 'Update the upper edge texture']],
                                           'true'),
                                          ([['name', 'texture'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'Upper edge texture']],
                                           edgeTextures),
                                          ([['name', 'update_down'],
                                            ['type', 'boolean'],
                                            ['_gui-text', 'Update the down edge texture']],
                                           'true'),
                                          ([['name', 'downtexture'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'Down edge texture']],
                                           edgeTextures)],
                        commandValue   = 'addEdge.py',
                        file           = directory + '/addEdge.inx',
                        subsubmenuText = 'Blocks')


def updateAddBackgroundBlock_inx(directory, textures):
    updateEffectInxFile(nameValue    = 'Convert into Background Block',
                        id           = 'org.ekips.filter.addbackgroundblock',
                        dependencies = [('executable', 'addBackgroundBlock.py'),
                                        ('executable', 'inkex.py')],
                        params       = [([['name', 'update'],
                                          ['type', 'boolean'],
                                          ['_gui-text', 'Update the block texture']],
                                         'true'),
                                        ([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue = 'addBackgroundBlock.py',
                        file         = directory + '/addBackgroundBlock.inx',
                        subsubmenuText = 'Blocks')

def updateAddDynamicBlock_inx(directory, textures):
    updateEffectInxFile(nameValue    = 'Convert into Dynamic Block',
                        id           = 'org.ekips.filter.adddynamicblock',
                        dependencies = [('executable', 'addDynamicBlock.py'),
                                        ('executable', 'inkex.py')],
                        params       = [([['name', 'update'],
                                          ['type', 'boolean'],
                                          ['_gui-text', 'Update the block texture']],
                                         'true'),
                                        ([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue = 'addDynamicBlock.py',
                        file         = directory + '/addDynamicBlock.inx',
                        subsubmenuText = 'Blocks')

def updateAddNormalBlock_inx(directory, textures):
    updateEffectInxFile(nameValue    = 'Convert into Normal Block',
                        id           = 'org.ekips.filter.addnormalblock',
                        dependencies = [('executable', 'addNormalBlock.py'),
                                        ('executable', 'inkex.py')],
                        params       = [([['name', 'update'],
                                          ['type', 'boolean'],
                                          ['_gui-text', 'Update the block texture']],
                                         'true'),
                                        ([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures)],
                        commandValue = 'addNormalBlock.py',
                        file         = directory + '/addNormalBlock.inx',
                        subsubmenuText = 'Blocks')

def updateAddSprite_inx(directory, sprites):
    updateEffectInxFile(nameValue      = 'Convert into Sprite',
                        id             = 'org.ekips.filter.addsprite',
                        dependencies   = [('executable', 'addSprite.py'),
                                          ('executable', 'inkex.py')],
                        params         = [([['name', 'name'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'Sprite name']],
                                           sprites),
                                          ([['name', 'update'],
                                            ['type', 'boolean'],
                                            ['_gui-text', 'Update the sprite properties below']],
                                           'true'),
                                          ([['name', 'z'],
                                            ['type', 'int'],
                                            ['min', '-1'],
                                            ['max', '1'],
                                            ['_gui-text', 'Sprite z']],
                                           '-1'),
                                          ([['name', 'angle'],
                                            ['type', 'float'],
                                            ['min',  '0.0'],
                                            ['max',  '360.0'],
                                            ['_gui-text', 'Rotation angle (in degree)']],
                                           0.0),
                                          ([['name', 'reversed'],
                                            ['type', 'boolean'],
                                            ['_gui-text', 'Reverse the sprite (x axis)']],
                                           'false')],
                        commandValue   = 'addSprite.py',
                        file           = directory + '/addSprite.inx',
                        subsubmenuText = 'Entities')

def updateAddParticleSource_inx(directory, particleSources):
    updateEffectInxFile(nameValue      = 'Convert into Particle Source',
                        id             = 'org.ekips.filter.addparticlesource',
                        dependencies   = [('executable', 'addParticleSource.py'),
                                          ('executable', 'inkex.py')],
                        params         = [([['name', 'type'],
                                            ['type', 'enum'],
                                            ['_gui-text', 'Particle source type']],
                                           particleSources)],
                        commandValue   = 'addParticleSource.py',
                        file           = directory + '/addParticleSource.inx',
                        subsubmenuText = 'Entities')

def updateInx(content, directory):
    if content is not None:
        exec(content)
    else:
        from listAvailableElements import textures, edgeTextures, sprites
        from listAvailableElements import particleSources, rversions

    updateChangeBlockTexture_inx(directory, textures)
    updateAddEdge_inx(directory, edgeTextures)
    updateAddSprite_inx(directory, sprites)
    updateAddParticleSource_inx(directory, particleSources)
    updateAddBackgroundBlock_inx(directory, textures)
    updateAddDynamicBlock_inx(directory, textures)
    updateAddNormalBlock_inx(directory, textures)
