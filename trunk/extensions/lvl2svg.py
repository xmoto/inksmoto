from level   import Level
from factory import Factory
from stats   import Stats
import parsers
import logging, log

def lvl2svg(openFile):
    log.eraseLogFile()
    printWelcomeMessage()

    level  = Level()
    parser = Factory().createObject('XmlLvl_parser')

    parser.parse(openFile, level)
    level.generateSvgContent()

    logging.info(Stats().printReport())

if __name__ == "__main__":
    import sys

    if len(sys.arvg) > 1:
        svgFile = open(sys.argv[-1])
    else:
        svgFile = sys.stdin

    svg2lvl(svgFile)
