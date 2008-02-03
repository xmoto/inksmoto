from lxml import etree
from lxml.etree import Element, SubElement, ElementTree
import logging, log

def createInxHead(nameValue, id, dependencies, params):
    """ create the header of the inx file

    create the name, id, dependencies and params.    
    """
    root = Element('inkscape-extension')

    # add the name of the extension
    name = SubElement(root, 'name')
    name.text = nameValue

    # add its id
    idNode = SubElement(root, 'id')
    idNode.text = id

    # add its dependencies, which are of two types:
    #  executables
    #  extension
    for typeDep, text in dependencies:
        dependency = SubElement(root, 'dependency')
        dependency.set('type',     typeDep)
        dependency.set('location', 'extensions')
	dependency.text = text

    # add its attributes.
    for attributes, text in params:
        paramNode = SubElement(root, 'param')
        for name, value in attributes:
            paramNode.set(name, value)

        if type(text) == dict:
            for itemValue in text.keys():
                item      = SubElement(paramNode, 'item')
		item.text = '%s' % itemValue
        elif type(text) == list:
            for itemValue in text:
                item     = SubElement(paramNode, 'item')
		item.text = '%s' % itemValue
        else:
	    paramNode.text = str(text)

    return root

def createInxFoot(root, commandValue, file):
    script = SubElement(root, 'script')
    command = SubElement(script, 'command')
    command.set('reldir',      'extensions')
    command.set('interpreter', 'python')
    command.text = commandValue

    f = open(file, 'w')
    ElementTree(root).write(f)
    f.close()
    
def updateOutputInxFile(**kwargs):
    nameValue    = kwargs['nameValue']
    id           = kwargs['id']
    dependencies = kwargs['dependencies']
    params       = kwargs['params']
    commandValue = kwargs['commandValue']
    file         = kwargs['file']

    extensionText     = kwargs['extensionText']
    mimeTypeText      = kwargs['mimeTypeText']
    _fileTypeNameText = kwargs['_fileTypeNameText']
    _fileTypeTooltip  = kwargs['_fileTypeTooltip']

    root = createInxHead(nameValue, id, dependencies, params)

    output = SubElement(root, 'output')

    for name, text in [('extension',        extensionText),
                       ('mimetype',         mimeTypeText),
                       ('_filetypename',    _fileTypeNameText),
                       ('_filetypetooltip', _fileTypeTooltip),
                       ('dataloss',         'TRUE')]:
        node = SubElement(output, name)
	node.text = text

    createInxFoot(root, commandValue, file)

def updateEffectInxFile(**kwargs):
    nameValue    = kwargs['nameValue']
    id           = kwargs['id']
    dependencies = kwargs['dependencies']
    params       = kwargs['params']
    commandValue = kwargs['commandValue']
    file         = kwargs['file']

    subsubmenuText = kwargs['subsubmenuText']

    root   = createInxHead(nameValue, id, dependencies, params)

    effect = SubElement(root, 'effect')

    object_type = SubElement(effect, 'object-type')
    object_type.text = 'path'

    effects_menu = SubElement(effect, 'effects-menu')

    submenu = SubElement(effects_menu, 'submenu')
    submenu.set('_name', 'X-moto')

    subsubmenu = SubElement(submenu, 'submenu')
    subsubmenu.set('_name', subsubmenuText)

    createInxFoot(root, commandValue, file)

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


def updateChangeBlockType_inx(directory, textures):
    updateEffectInxFile(nameValue    = 'Change Block Type',
                        id           = 'org.ekips.filter.changeblocktype',
                        dependencies = [('executable', 'changeBlockType.py'),
                                        ('executable', 'inkex.py')],
                        params       = [([['name', 'update'],
                                          ['type', 'boolean'],
                                          ['_gui-text', 'Update the block texture']],
                                         'true'),
                                        ([['name', 'texture'],
                                          ['type', 'enum'],
                                          ['_gui-text', 'Block texture']],
                                         textures),
                                        ([['name', 'block_description'],
                                          ['type', 'description']],
                                         "Uncheck both to convert into normal block."),
                                        ([['name', 'background'],
                                          ['type', 'boolean'],
                                          ['_gui-text', 'Convert in background block']],
                                         'false'),
                                        ([['name', 'dynamic'],
                                          ['type', 'boolean'],
                                          ['_gui-text', 'Convert in dynamic block']],
                                         'false')],
                        commandValue = 'changeBlockType.py',
                        file         = directory + '/changeBlockType.inx',
                        subsubmenuText = 'Blocks')

def updateAddSprite_inx(directory, sprites):
    updateEffectInxFile(nameValue      = 'Convert into Sprite',
                        id             = 'org.ekips.filter.addsprite',
                        dependencies   = [('executable', 'addSprite.py'),
                                          ('executable', 'inkex.py')],
                        params         = [([['name', 'updatesprite'],
                                            ['type', 'boolean'],
                                            ['_gui-text', 'Update the sprite texture']],
                                           'true'),
                                          ([['name', 'name'],
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
                                           'false'),
                                          ([['name', 'updatedims'],
                                            ['type', 'boolean'],
                                            ['_gui-text', 'Update the sprite dimensions']],
                                           'false'),
                                          ([['name', 'width'],
                                            ['type', 'float'],
                                            ['min',  '0.1'],
                                            ['max',  '10.0'],
                                            ['_gui-text', 'Sprite width']],
                                           1.0),
                                          ([['name', 'height'],
                                            ['type', 'float'],
                                            ['min',  '0.1'],
                                            ['max',  '10.0'],
                                            ['_gui-text', 'Sprite height']],
                                           1.0),
                                          ([['name', 'r'],
                                            ['type', 'float'],
                                            ['min',  '0.1'],
                                            ['max',  '5.0'],
                                            ['_gui-text', 'Sprite collision radius']],
                                           0.5)],
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
        from listAvailableElements import particleSources

    updateChangeBlockTexture_inx(directory, textures)
    updateAddEdge_inx(directory, edgeTextures)
    updateAddSprite_inx(directory, sprites)
    updateAddParticleSource_inx(directory, particleSources)
    updateChangeBlockType_inx(directory, textures)