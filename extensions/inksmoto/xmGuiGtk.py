#!/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import log, logging
import sys

try:
    import gtk
    import gtk.glade
except:
    log.outMsg("You need to install PyGtk")
    sys.exit(1)

from os.path import join
from xmotoTools import getSystemDir, getExistingImageFullPath
from xmotoTools import alphabeticSortOfKeys
from availableElements import AvailableElements

TEXTURES = AvailableElements()['TEXTURES']
EDGETEXTURES = AvailableElements()['EDGETEXTURES']
SPRITES = AvailableElements()['SPRITES']
PARTICLESOURCES = AvailableElements()['PARTICLESOURCES']

EDGETEXTURES['_None_'] = {'file':'none.png'}
TEXTURES['_None_'] = {'file':'none.png'}
SPRITES['_None_'] = {'file':'none.png'}

def quit(widget=None):
    """ the widget param is present when called from a gtk signal
    """
    gtk.main_quit()

def mainLoop():
    gtk.main()

def errorMessageBox(msg):
    gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL,
                      type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                      message_format=msg).run()

def createWindow(gladeFile, windowName):
    return gtk.glade.XML(join(getSystemDir(), 'glade', gladeFile),
                         windowName)

def addImageToButton(button, imgFile):
    img = gtk.Image()
    img.set_from_file(imgFile)
    button.set_image(img)

def resetColor(button):
    button.set_color(gtk.gdk.color_parse('white'))
    button.set_alpha(65535)

class bitmapSelectWindow:
    def __init__(self, title, bitmaps):
        self.selectedImage = None

        wTree = createWindow('bitmapSelection.glade', 'bitmapSelection')
        self.window = wTree.get_widget('bitmapSelection')
        self.window.set_title(title)
        self.window.connect("destroy", gtk.main_quit)

        layout = wTree.get_widget('bitmapsLayout')
        nbColumns = 4
        keys = alphabeticSortOfKeys(bitmaps.keys())

        self.window.set_size_request(108*nbColumns+16*2, 108*nbColumns+16*2)
        layout = wTree.get_widget('bitmapsLayout')
        layout.set_size(8 + 108 * nbColumns,
                        8 + (108+24) * (1 + (len(keys) / nbColumns)))

        counter = 0
        for name in keys:
            imgFile = getExistingImageFullPath(bitmaps[name]['file'])
            try:
                button = gtk.Button()
                addImageToButton(button, imgFile)
                button.connect("clicked", self.buttonClicked, name)

                label = gtk.Label(name)
                label.set_justify(gtk.JUSTIFY_CENTER)
                label.set_size_request(108, 24)

                x = 8 + 108 * (counter % nbColumns)
                y = 8 + (108+24) * (counter / nbColumns)
                layout.put(button, x, y)
                layout.put(label, x, y + 108)
            except Exception, e:
                logging.info("Can't create bitmap from %s\n%s" % (imgFile, e))
            else:
                counter += 1

    def run(self):
        self.window.show_all()
        gtk.main()
        return self.selectedImage

    def buttonClicked(self, widget, imgName):
        self.selectedImage = imgName
        self.window.destroy()
        gtk.main_quit()
