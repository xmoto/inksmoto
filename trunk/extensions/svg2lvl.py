# licence: GPL V2
# author:  Emmanuel Gorse

from inksmoto import log
import logging
from inksmoto.factory import Factory
from inksmoto.xmotoTools import getHomeDir
from os.path import join
from shutil  import copyfile
from inksmoto.inkex   import NSS
# register parsers in the factory
from inksmoto import parsers

def svg2lvl(svgFileName, lvlFileName=None):
    #log.eraseLogFile()

    # save the svg into ~/.inkscape
    lastName = join(getHomeDir(), 'last.svg')
    try:
        copyfile(svgFileName, lastName)
    except Exception, e:
        logging.info("Last svg not saved in %s.\n%s" % (lastName, e))

    parser = Factory().createObject('XmlSvg_parser')

    svgFile = open(svgFileName, 'r')
    level = parser.parse(svgFile)

    if lvlFileName != None:
        lvlfile = open(lvlFileName, 'w')
    else:
        lvlfile = None
    level.generateLvlContent(lvlfile)

    svgFile.close()
    if lvlfile is not None:
        lvlfile.close()

if __name__ == "__main__":
    import sys
    NSS[u'xmoto'] = u'http://xmoto.tuxfamily.org/'

    try:
        svg2lvl(sys.argv[-1])
    except Exception, exc:
        log.outMsg(str(exc))
