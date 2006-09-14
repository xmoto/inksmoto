from singleton import Singleton
import logging, log

class Stats:
    # FIXME::make independant of entities, blocks and zones...
    __metaclass__ = Singleton

    def __init__(self):
        self.reinitStats()

    def reinitStats(self):
        self.entitiesName = []
        self.blockVertex  = {}
        self.zonesName    = []
        self.nbVertex     = 0
        self.nbOptimizedVertex = 0

    def addZone(self, name):
        self.zonesName.append(name)

    def addEntity(self, name):
        self.entitiesName.append(name)

    def addBlock(self, name):
        self.blockVertex[name] = 0

    def addVertice(self, blockName):
        self.blockVertex[blockName] += 1
        self.nbVertex += 1
    
    def addOptimizedVertice(self, blockName):
        self.nbOptimizedVertex += 1

    def getNbEntity(self):
        return len(self.entitiesName)

    def getNbBlock(self):
        return len(self.blockVertex.keys())

    def getNbZone(self):
        return len(self.zonesName)

    def printReport(self):
        report = "\n---------------------------------------\n"
        report += "Stats:\n"

        for zoneName in self.zonesName:
            report += "zone %s\n" % zoneName
        for entityName in self.entitiesName:
            report += "entity %s\n" % entityName
        for blockName, nbVertex in self.blockVertex.iteritems():
            report += "%d element in the block %s\n" % (nbVertex, blockName)

        report += "\n%d zones in the level\n"  % self.getNbZone()
        report += "%d entitys in the level\n"  % self.getNbEntity()
        report += "%d blocks in the level\n"   % self.getNbBlock()
        report += "%d vertex in the level (%d before optimization)\n\n" % (self.nbOptimizedVertex, self.nbVertex)

        report += "---------------------------------------\n"
        
        return report
