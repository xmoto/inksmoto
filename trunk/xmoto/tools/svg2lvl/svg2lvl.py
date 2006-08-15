# licence: GPL V2
# author:  Emmanuel Gorse

from level   import Level
from factory import Factory
from stats   import Stats
import parsers
import logging, log

def printWelcomeMessage():
    print "Hi! Welcome to the svg to lvl converter by Emmanuel Gorse."
    print "(Inspired from Erik-Ryb's one)."
    print "This program converts a svg-file made with Inkscape to a X-Moto level-file."
    print "To convert a file, make sure that the svg-file is in the same folder as this program."
    print ""


def svg2lvl(svgname, newWidth, levelname, scriptName):
    printWelcomeMessage()

    level  = Level()
    parser = Factory().createObject('XML_parser')

    parser.parse(svgname, level)
    level.generateLvlFile(levelname, newWidth, scriptName)

    print Stats().printReport()
    
if __name__ == "__main__":
    import sys
    
    nbArg = len(sys.argv)
    if nbArg < 4:
        print "usage: %s svgname newwidth levelname" % sys.argv[0]
    else:
        svgName   = sys.argv[1]
        newWidth  = sys.argv[2]
        levelName = sys.argv[3]

        if nbArg == 5:
            scriptName = sys.argv[4]
        else:
            scriptName = None
    
        svg2lvl(svgName, newWidth, levelName, scriptName)
