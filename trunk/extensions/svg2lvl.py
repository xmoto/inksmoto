# licence: GPL V2
# author:  Emmanuel Gorse

from factory import Factory
from stats   import Stats
from xmotoTools import getHomeInkscapeExtensionsDir
from os.path import join
from shutil  import copyfile
from inkex   import NSS
import parsers
import logging, log

def svg2lvl(svgname, lvlfileName=None):
    #log.eraseLogFile()

    # save the svg into ~/.inkscape
    lastName = join(getHomeInkscapeExtensionsDir(), 'last.svg')
    try:
        copyfile(svgname, lastName)
    except Exception, e:
        logging.info("Last svg not saved in %s.\n%s" % (lastName, e))

    parser = Factory().createObject('XmlSvg_parser')

    svgFile = open(svgname, 'r')
    level = parser.parse(svgFile)

    if lvlfileName != None:
        lvlfile = open(lvlfileName, 'w')
    else:
        lvlfile = None
    level.generateLvlContent(lvlfile)

    logging.info(Stats().printReport())

    svgFile.close()
    if lvlfile is not None:
        lvlfile.close()

if __name__ == "__main__":
    import sys
    from xmotoTools import addHomeDirInSysPath
    addHomeDirInSysPath()

    svgFile = sys.argv[-1]
    NSS[u'xmoto'] = u'http://xmoto.tuxfamily.org/'

    try:
        svg2lvl(svgFile)
    except Exception, e:
        log.outMsg(str(e))
