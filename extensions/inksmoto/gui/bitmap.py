import os
import re
from pathlib import Path

from typing import OrderedDict

from inksmoto.xmotoTools import get_bitmap_dir
from .gtk import Gtk


ALLOWED_BITMAP_EXTENSIONS = ['.jpg', '.jpeg', '.png']

BITMAP_NONE = 'None'
# TODO(Nikekson): Load the __missing__.png image instead
IMAGE_MISSING = Gtk.IconTheme.get_default().load_icon('image-missing', 96, 0)
NOTSET_BITMAP = ['_None_', '', None, 'None']


def load_bitmap_list() -> OrderedDict[str, str]:
    bitmaps = OrderedDict()

    # TODO(Nikekson): This code is duplicated a few times in the codebase
    bitmap_dir = get_bitmap_dir()
    if not bitmap_dir:
        raise RuntimeError("Failed to get bitmap directory")

    for file in os.listdir(bitmap_dir):
        path = Path(file)
        if path.suffix.lower() in ALLOWED_BITMAP_EXTENSIONS:
            name = re.sub('(.*)(_[0-9]+)', r'\1', path.stem)
            bitmaps[name] = file

    bitmaps = OrderedDict(sorted(bitmaps.items(), key=lambda e: e[0].lower()))

    bitmaps[BITMAP_NONE] = None
    bitmaps.move_to_end(BITMAP_NONE, last=False)

    return bitmaps
