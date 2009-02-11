from inksmoto.xmotoExtensionTkinter import XmExtTkLevel
from inksmoto.xmotoTools import createIfAbsent, alphabeticSortOfKeys, getValue
from inksmoto.inkex import NSS
from inksmoto.listAvailableElements import SPRITES, MUSICS
from inksmoto import xmGui
from inksmoto.factory import Factory

class AddOtherLevelInfos(XmExtTkLevel):
    def __init__(self):
        XmExtTkLevel.__init__(self)
        self.defaultScale = 1

    def afterHook(self):
        # update all the strawberries, wrecker and flower in the svg
        # with their new collision radius
        for typeid in ['Strawberry', 'Wrecker', 'EndOfLevel']:
            search = '//*[contains(@xmoto:xmoto_label, "typeid=%s")]' % typeid
            nodes = self.document.xpath(search, namespaces=NSS)
            for node in nodes:
                self.handlePath(node)

    def updateLabelData(self):
        for name, value in self.replacement.iteritems():
            self.label['remplacement'][name] = value.get()

        self.label['level']['music'] = self.music.get()

    def createWindow(self):
        createIfAbsent(self.label, 'level')
        createIfAbsent(self.label, 'remplacement')

        f = Factory()
        xmGui.defineWindowHeader('Other level properties')

        bitmapSize = xmGui.getBitmapSizeDependingOnScreenResolution()

        self.replacement = {}
        for name, useScale in [('Strawberry', True), ('Wrecker', True),
                               ('Flower', True), ('Star', False)]:
            f.createObject('XmLabel', name + ':')

            sprite = getValue(self.label, 'remplacement',
                              name, default=name)
            self.replacement[name] = f.createObject('XmBitmap',
                                                    SPRITES[sprite]['file'],
                                                    sprite,
                                                    toDisplay='sprites',
                                                    callback=self.updateBitmap,
                                                    buttonName=name,
                                                    size=bitmapSize)

            if useScale == True:
                value = getValue(self.label, 'remplacement',
                                 name+'Scale', default=self.defaultScale)
                scale = f.createObject('XmScale', value, label=name+' scale:',
                                       from_=0.1, to=10, resolution=0.1,
                                       default=self.defaultScale)
                self.replacement[name+'Scale'] = scale

        value = getValue(self.label, 'level', 'music')
        self.music = f.createObject('XmListbox',
                                    value, label='Level music',
                                    items=['None']+alphabeticSortOfKeys(MUSICS))

    def updateBitmap(self, imgName, buttonName):
        self.replacement[buttonName].update(imgName, SPRITES)

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddOtherLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
