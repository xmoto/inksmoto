import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from inksmoto.xmExtGtk import XmExtGtkLevel, WidgetInfos
from inksmoto.xmotoTools import createIfAbsent, checkId, getValue, getHomeDir
from inksmoto.availableElements import AvailableElements
from inksmoto import xmGuiGtk
from os.path import expanduser

TEXTURES = AvailableElements()['TEXTURES']

class AddLevelInfos(XmExtGtkLevel):
    def getWindowInfos(self):
        gladeFile = "addLevelInfos.glade"
        windowName = "addLevelInfos"
        return (gladeFile, windowName)

    def getWidgetsInfos(self):
        return {'smooth': WidgetInfos('level', 'smooth', 9),
                'lua': WidgetInfos('level', 'lua', expanduser('~')),
                'id': WidgetInfos('level', 'id', ''),
                'name': WidgetInfos('level', 'name', ''),
                'author': WidgetInfos('level', 'author', ''),
                'desc': WidgetInfos('level', 'desc', ''),
                'tex': WidgetInfos('level', 'tex', '_None_')}

    def getSignals(self):
        return {'on_tex_clicked': self.updateBitmap,
                'on_resetScript_clicked': self.resetScript}

    def updateLabelData(self):
        if ('level' not in self.label or 'id' not in self.label['level']
            or 'name' not in self.label['level']
            or len(self.label['level']['id']) == 0
            or len(self.label['level']['name']) == 0):
            raise Exception('You have to set the level id and name')

        if not checkId(self.label['level']['id']):
            msg = "The level id can only contain alphanumeric characters and _"
            raise Exception(msg)

    def updateBitmap(self, widget):
        imgName = xmGuiGtk.BitmapSelectWindow('Texture Selection',
                                              TEXTURES).run()  # Corrected method name

        if imgName is not None:
            xmGuiGtk.addImgToBtn(widget, self.get('texLabel'),
                                 imgName, TEXTURES)

    def resetScript(self, widget):
        lua = self.get('lua')
        lua.set_current_folder(getHomeDir())

def run():
    ext = AddLevelInfos()
    ext.affect()
    return ext

if __name__ == '__main__':
    run()
