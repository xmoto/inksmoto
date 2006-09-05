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

def svg2lvl(svgname, newWidth, scriptName, smoothitude, levelId):
    log.eraseLogFile()
    printWelcomeMessage()

    level  = Level()
    parser = Factory().createObject('XML_parser')

    parser.parse(svgname, level)
    level.generateLvlContent(levelId, newWidth, scriptName, smoothitude)

    logging.info(Stats().printReport())

if __name__ == "__main__":
    import optparse, sys
    optionParser = optparse.OptionParser(usage="usage: %prog --width=WIDTH --smooth=PERCENT --name=LEVELID [--lua=SCRIPTFILE] svgFile")
    optionParser.add_option("--width",  dest="width",  type="float",  help="level width in xmoto units")
    optionParser.add_option("--smooth", dest="smooth", type="float",  help="smooth percent [1-100]")
    optionParser.add_option("--lua",    dest="lua",    type="string", help="lua script file (if any)")
    optionParser.add_option("--name",   dest="name",   type="string", help="level id")
    options, argv = optionParser.parse_args(sys.argv[1:])

    if options.width == None or options.smooth == None or options.name == None:
        optionParser.error("missing option [width, smooth, name]")

    svgFile = sys.argv[-1]

    if options.lua == '':
        options.lua = None

    svg2lvl(svgFile, options.width, options.lua, options.smooth, options.name)
        
        
        
        
        
        
        
