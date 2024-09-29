# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
# pyright: reportAttributeAccessIssue=false

import os
import sys
from typing import Callable
import gi

try:
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GObject as GObject
except ImportError or ValueError as e:
    print(e)
    sys.exit(1)


GLADE_TEMPLATE_DIRECTORY = os.path.join(os.path.dirname(__file__), "glade")


def _bind_template_widgets(cls: type[Gtk.Window]):
    for attr, value in cls.__annotations__.items(): # pyright: ignore[reportAny]
        if isinstance(value, type(Gtk.Widget)) and not hasattr(cls, attr):
            setattr(cls, attr, Gtk.Template.Child(name=attr))  # pyright: ignore[reportCallIssue]


def _build_template[T: Gtk.Window](cls: type[T], filename: str):
    template_path = os.path.join(GLADE_TEMPLATE_DIRECTORY, filename)
    Gtk.Template(filename=template_path)(cls)


def window_template(filename: str) -> Callable[[type[Gtk.Window]], type[Gtk.Window]]:
    def template(cls: type[Gtk.Window]) -> type[Gtk.Window]:
        real_init = cls.__init__

        def init_wrapper(self: Gtk.Window, *args, **kwargs):
            _bind_template_widgets(cls)
            _build_template(cls, filename)
            real_init(self, *args, **kwargs)

        cls.__init__ = init_wrapper
        return cls

    return template


def window_hints(cls: type[Gtk.Window]) -> type[Gtk.Window]:
    real_init = cls.__init__

    def init(self, *args, **kwargs):
        real_init(self, *args, **kwargs)
        self.set_type_hint(Gdk.Window.WindowTypeHint.DIALOG)

    cls.__init__ = init
    return cls


def create_window(window_class: type[Gtk.Window]):
    window = window_class()
    _ = window.connect("destroy", Gtk.main_quit)
    window.show_all()

    Gtk.main()
