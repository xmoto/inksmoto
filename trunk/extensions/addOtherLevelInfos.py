from xmotoExtensionTkinter import XmotoExtTkLevel, XmListbox
from xmotoExtensionTkinter import XmBitmap, XmScale, XmLabel
from xmotoTools import createIfAbsent, alphabeticSortOfKeys
from inkex import NSS
from listAvailableElements import SPRITES, MUSICS

class AddOtherLevelInfos(XmotoExtTkLevel):
    def __init__(self):
        XmotoExtTkLevel.__init__(self)
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

        self.defineWindowHeader('Other level properties')

        bitmapSize = self.getBitmapSizeDependingOnScreenResolution()

        self.replacement = {}
        for name, useScale in [('Strawberry', True), ('Wrecker', True),
                               ('Flower', True), ('Star', False)]:
            XmLabel(self.frame, name + ':')

            sprite = self.getValue(self.label, 'remplacement',
                                   name, default=name)
            self.replacement[name] = XmBitmap(self.frame,
                                              SPRITES[sprite]['file'],
                                              sprite,
                                              self.spriteSelectionWindow,
                                              buttonName=name,
                                              size=bitmapSize)

            if useScale == True:
                scale = self.getValue(self.label, 'remplacement',
                                      name+'Scale', default=self.defaultScale)
                scale = XmScale(self.frame, scale, label=name+' scale:',
                                from_=0.1, to=10, resolution=0.1,
                                default=self.defaultScale)
                self.replacement[name+'Scale'] = scale

        self.music = XmListbox(self.frame,
                               self.getValue(self.label, 'level', 'music'),
                               label='Level music',
                               items=['None']+alphabeticSortOfKeys(MUSICS))

    def bitmapSelectionWindowHook(self, imgName, buttonName):
        self.replacement[buttonName].update(imgName, SPRITES)

def run():
    """ use a run function to be able to call it from the unittests """
    ext = AddOtherLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
