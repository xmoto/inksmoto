# licence: GPL V2
# author:  Emmanuel Gorse

from level   import Level
from factory import Factory
from stats   import Stats
import parsers
import logging, log

def printWelcomeMessage():
    logging.info("Hi! Welcome to the svg to lvl converter by Emmanuel Gorse.")
    logging.info("(Inspired from Erik-Ryb's one).")
    logging.info("This program converts a svg-file made with Inkscape to a X-Moto level-file.")
    logging.info("To convert a file, make sure that the svg-file is in the same folder as this program.")
    logging.info("")

def svg2lvl(svgname, options):
    log.eraseLogFile()
    printWelcomeMessage()

    level  = Level()
    parser = Factory().createObject('XML_parserSvg')

    svgFile = open(svgname, 'r')

    parser.parse(svgFile, level)
    level.generateLevelDataFromSvg(options)
    level.generateLvlContent()

    logging.info(Stats().printReport())

if __name__ == "__main__":
    import optparse, sys
    optionParser = optparse.OptionParser(usage="usage: %prog --width=WIDTH --smooth=PERCENT --name=LEVELID [--lua=SCRIPTFILE] svgFile")
    optionParser.add_option("--smooth",   dest="smooth",   type="float",  help="smooth percent [1-100]")
    optionParser.add_option("--lua",      dest="lua",      type="string", help="lua script file (if any)")
    optionParser.add_option("--id",       dest="id",       type="string", help="level id")
    optionParser.add_option("--name",     dest="name",     type="string", help="level name")
    optionParser.add_option("--author",   dest="author",   type="string", help="author")
    optionParser.add_option("--desc",     dest="desc",     type="string", help="description")
    optionParser.add_option("--sky",      dest="sky",      type="string", help="sky")
    optionParser.add_option("--rversion", dest="rversion", type="string", help="required xmoto version")

    
    options, argv = optionParser.parse_args(sys.argv[1:])

    if options.smooth == None or options.id == None:
        optionParser.error("missing option [smooth, id]")

    svgFile = sys.argv[-1]

    if options.lua == '' or options.lua == 'None':
        options.lua = None

    svg2lvl(svgFile, options)
