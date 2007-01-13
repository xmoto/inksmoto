from level   import Level
from factory import Factory
from stats   import Stats
import parsers
import logging, log

# to be done...


def lvl2svg(svgname, newWidth, levelname, scriptName):
#    printWelcomeMessage()

    level = Level()
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
