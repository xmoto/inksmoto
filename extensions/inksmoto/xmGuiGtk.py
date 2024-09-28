#!/bin/python3
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com
"""

from gi.repository import Gtk, GdkPixbuf, Gdk
import logging
import sys

from os.path import join, exists
from .xmotoTools import getSystemDir, getExistingImageFullPath
from .xmotoTools import alphabeticSortOfKeys, getHomeDir
from .availableElements import AvailableElements

import warnings
import re

# Suppress specific warnings from IMKClient and IMKInputSession
def suppress_imk_warnings(message, category, filename, lineno, file=None, line=None):
    return re.search(r'IMKClient|IMKInputSession', str(message))

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*IMKClient.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*IMKInputSession.*")

TEXTURES = AvailableElements()['TEXTURES']
EDGETEXTURES = AvailableElements()['EDGETEXTURES']
SPRITES = AvailableElements()['SPRITES']
PARTICLESOURCES = AvailableElements()['PARTICLESOURCES']

EDGETEXTURES['_None_'] = {'file':'none.png'}
TEXTURES['_None_'] = {'file':'none.png'}
SPRITES['_None_'] = {'file':'none.png'}

def quit(widget=None):
    """ the widget param is present when called from a gtk signal."""
    Gtk.main_quit()

def mainLoop():
    Gtk.main()

def errorMessageBox(msg):
    dlg = Gtk.MessageDialog(parent=None, flags=Gtk.DialogFlags.MODAL,
                            type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE,
                            message_format=msg)
    dlg.run()
    dlg.destroy()

def createWindow(gladeFile, windowName):
    # Setup logger with file handler
    file_handler = logging.FileHandler('/tmp/inkscape_extension.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Add the file handler
    logger.addHandler(file_handler)

    # Log some messages
    try:
        # Create the path to the Glade file in the user's home directory
        path = join(getHomeDir(), 'inksmoto', 'glade', gladeFile)
        builder = Gtk.Builder()
        # Try loading from the home directory
        if exists(path):
            try:
                builder.add_from_file(path)
                logging.info(f"Loaded Glade file from: {path}")
            except Exception as e:
                logger.error(f"Error loading Glade file from home directory: {e}")
                file_handler.flush()
                return None
        else:
            # Try loading from the system directory
            path = join(getSystemDir(), 'glade', gladeFile)
            if exists(path):
                try:
                    logger.info(f"Loading Glade file from {path}")
                    builder.add_from_file(path)
                    logger.info(f"Loaded Glade file from system directory: {path}")
                    file_handler.flush()
                except Exception as e:
                    logger.error(f"Error loading Glade file from system directory: {e}")
                    file_handler.flush()
                    return None
            else:
                logger.error(f"Glade file: {gladeFile} not found at: {path}.")
                file_handler.flush()
                return None

        # Return the window object based on windowName
        window = builder.get_object(windowName)
        if window is None:
            logger.error(f"Window '{windowName}' not found in the Glade file.")
            file_handler.flush()
        logger.debug(window)
        file_handler.flush()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        file_handler.flush()

    return builder

def addImgToBtn(button, label, imgName, bitmapDict):
    imgFile = bitmapDict[imgName]['file']
    imgFullFile = getExistingImageFullPath(imgFile)

    if imgFullFile is None:
        logging.warning("xmGuiGtk::addImgToBtn no image full path for %s: %s" % (imgName, imgFile))
        imgFile = '__missing__.png'
        imgFullFile = getExistingImageFullPath(imgFile)

    img = Gtk.Image()
    pixBuf = GdkPixbuf.Pixbuf.new_from_file(imgFullFile)
    img.set_from_pixbuf(pixBuf)

    button.set_image(img)
    label.set_text(imgName)

    img.show()

def resetColor(button):
    # Create a CSS provider
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(b"""
        button {
            background-color: #ffffff;
            color: #000000;
        }
    """)

    # Get the default screen and apply the style to the button
    style_context = button.get_style_context()
    style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    button.set_opacity(1.0)

class BitmapSelectWindow:
    def __init__(self, title, bitmaps):
        self.selectedImage = None

        # Assuming createWindow returns a Gtk.Builder
        wTree = createWindow('bitmapSelection.glade', 'bitmapSelection')
        self.window = wTree.get_object('bitmapSelection')  # get_object for GTK 3
        self.window.set_title(title)
        self.window.connect("destroy", Gtk.main_quit)

        self.keys = alphabeticSortOfKeys(list(bitmaps.keys()))

        store = Gtk.ListStore(str, GdkPixbuf.Pixbuf)
        store.clear()

        # skip the __biker__.png image used for PlayerStart
        self.keys = [key for key in self.keys if bitmaps[key]['file'][0:2] != '__']

        for name in self.keys:
            try:
                imgFile = bitmaps[name]['file']
                imgFullFile = getExistingImageFullPath(imgFile)
                if imgFullFile is None:
                    imgFile = '__missing__.png'
                    imgFullFile = getExistingImageFullPath(imgFile)
                pixBuf = GdkPixbuf.Pixbuf.new_from_file(imgFullFile)

                store.append([name, pixBuf])

            except Exception as e:
                logging.info("Can't create bitmap for %s\n%s" % (name, e))
                store.append([name, None])

        iconView = wTree.get_object('bitmapsView')  # get_object for Gtk.IconView
        iconView.set_model(store)
        iconView.set_text_column(0)
        iconView.set_pixbuf_column(1)
        iconView.set_columns(3)  # Adjust this number to how many bitmaps you want in a row
        iconView.connect("item-activated", self.bitmapSelected)

    def run(self):
        self.window.show_all()
        Gtk.main()
        return self.selectedImage

    def bitmapSelected(self, iconView, imageIdx):
        self.selectedImage = self.keys[imageIdx.get_indices()[0]]
        self.window.destroy()
        Gtk.main_quit()

