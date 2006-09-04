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
    import sys

    nbArg = len(sys.argv)
    if nbArg < 5:
        logging.info("usage: python %s --width=float --smooth=float --lua=[string] --name=string svgfile" % sys.argv[0])
    else:
        def getVal(string):
            return string[string.find('=')+1:]

        width  = float(getVal(sys.argv[1]))
        smooth = float(getVal(sys.argv[2]))
        lua    = getVal(sys.argv[3])
        if lua == '':
            lua = None
        name   = getVal(sys.argv[4])
        svg    = sys.argv[-1]

        svg2lvl(svg, width, lua, smooth, name)
        
        
        
        
        
        
        
