# licence: GPL V2
# author:  Emmanuel Gorse

from level   import Level
from factory import Factory
from stats   import Stats
from xmotoExtension import getInkscapeExtensionsDir
from os.path import join
from shutil import copyfile
import parsers
import logging, log

def svg2lvl(svgname, lvlfileName=None):
    #log.eraseLogFile()

    # save the svg into ~/.inkscape
    lastName = join(getInkscapeExtensionsDir(), 'last.svg')
    try:
        copyfile(svgname, lastName)
    except Exception:
        logging.info("Last svg not saved in %s" % lastName)

    level  = Level()
    parser = Factory().createObject('XML_parserSvg')

    svgFile = open(svgname, 'r')
    parser.parse(svgFile, level)
    level.generateLevelDataFromSvg()

    if lvlfileName != None:
        lvlfile = open(lvlfileName, 'w')
    else:
        lvlfile = None
    level.generateLvlContent(lvlfile)

    logging.info(Stats().printReport())

if __name__ == "__main__":
    import sys
    svgFile = sys.argv[-1]
    try:
        svg2lvl(svgFile)
    except Exception, e:
        log.writeMessageToUser(str(e))
