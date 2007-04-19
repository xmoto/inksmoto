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

def svg2lvl(svgname):
    log.eraseLogFile()
    printWelcomeMessage()

    level  = Level()
    parser = Factory().createObject('XML_parserSvg')

    svgFile = open(svgname, 'r')

    parser.parse(svgFile, level)
    level.generateLevelDataFromSvg()
    level.generateLvlContent()

    logging.info(Stats().printReport())

if __name__ == "__main__":
    import sys
    svgFile = sys.argv[-1]
    svg2lvl(svgFile)
