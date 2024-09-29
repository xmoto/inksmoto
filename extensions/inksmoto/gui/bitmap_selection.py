import os

from inksmoto.gui import bitmap
from inksmoto.gui.gtk import Gtk, Gdk, GObject
from inksmoto.xmotoTools import get_bitmap_dir

from gi.repository.GdkPixbuf import Pixbuf


# TODO(Nikekson): Rebuild this as a Glade template
class BitmapSelection(Gtk.Dialog):
    _NAME_COLUMN = 1

    __gsignals__ = {
        'item-selected': (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    def __init__(self, items, title=None, selected=None, parent=None):
        Gtk.Dialog.__init__(self)
        self.set_title(title)
        self.set_default_size(680, 500)
        self.set_transient_for(parent)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        self.selected = selected
        self.items = items

        menu = Gtk.Menu()
        menuitem = Gtk.MenuItem(label='Show in explorer')
        menu.append(menuitem)
        menuitem = Gtk.MenuItem(label='Properties')
        menu.append(menuitem)
        menu.show_all()

        liststore = Gtk.ListStore(Pixbuf, str, str)

        #liststore.set_sort_column_id(self._NAME_COLUMN, Gtk.SortType.ASCENDING)
        #liststore.set_sort_func(self._NAME_COLUMN, self.sort_func, None)

        self.filter = liststore.filter_new()
        self.filter.set_visible_func(self.filter_func)

        self.iconview = Gtk.IconView()
        #self.iconview.set_model(liststore)
        self.iconview.set_model(self.filter)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(self._NAME_COLUMN)
        self.iconview.set_tooltip_column(2)
        self.iconview.set_item_width(96)
        self.iconview.set_activate_on_single_click(False)

        self.iconview.connect('selection-changed', self.on_selection_changed)
        self.iconview.connect('item-activated', self.on_item_activated)
        self.iconview.connect_object('button-press-event', self.on_button_press, menu) # context menu

        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text('Search for a texture (Ctrl-F)')
        self.search.connect('search-changed', self.on_search_change)
        self.search.connect('key-press-event', self.on_key_pressed_on_search)
        self.vbox.pack_start(self.search, False, False, 2)
        self.search_text = ''

        # We could use Gtk.Dialog.add_button here but we want
        # to use the Gtk.ButtonBox, which doesn't have that
        buttonbox = Gtk.ButtonBox()
        buttonbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        buttonbox.set_spacing(2)
        buttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        self.vbox.pack_end(buttonbox, False, False, 2)

        button = Gtk.Button.new_from_icon_name("gtk-cancel", Gtk.IconSize.BUTTON)
        button.set_label('Cancel')
        button.connect('clicked', lambda _: self.emit('response', Gtk.ResponseType.CANCEL))
        buttonbox.add(button)

        button = Gtk.Button.new_from_icon_name("gtk-ok", Gtk.IconSize.BUTTON)
        button.set_label('OK')
        button.connect('clicked', lambda _: self.emit('response', Gtk.ResponseType.OK))
        buttonbox.add(button)

        self.connect('response', self.on_response)

        self.scrolled_win = Gtk.ScrolledWindow(hexpand=True)
        self.scrolled_win.add(self.iconview)
        self.scrolled_win.connect('key-press-event', self.on_key_pressed_on_scrolledwin)
        self.vbox.pack_start(self.scrolled_win, True, True, 0)

        self.add_items(items, liststore)
        self.show_all()
        self.scroll_to_index(self.lookup_item_index(self.selected))

    def scroll_to_index(self, index):
        path = Gtk.TreePath(index)
        self.select_item(path)
        self.iconview.scroll_to_path(path, False, 0, 0)

    def select_item(self, path: int | Gtk.TreePath):
        if type(path) == int:
            path = Gtk.TreePath(path)
        self.iconview.set_cursor(path, None, False)
        self.iconview.select_path(path)

    def filter_func(self, model, iter, _):
        name = model.get_value(iter, self._NAME_COLUMN)
        return self.search_text.lower() in name.lower()

    #def sort_func(self, model, a, b, _):
    #    sort_col, _ = model.get_sort_column_id()
    #    x = model.get_value(a, sort_col).lower()
    #    y = model.get_value(b, sort_col).lower()
    #    return (x > y) - (x < y)

    def add_items(self, items, liststore):
        for name, filename in items.items():
            if filename is None:
                pixbuf = bitmap.IMAGE_MISSING
            else:
                bitmap_dir = get_bitmap_dir()
                if not bitmap_dir:
                    raise RuntimeError("Failed to get bitmap directory")

                path = os.path.join(bitmap_dir, filename)
                pixbuf = Pixbuf.new_from_file_at_size(path, 96, 96)

            liststore.append([pixbuf, name, filename])

    def on_key_pressed_on_scrolledwin(self, _, event):
        mod_mask = Gdk.ModifierType.CONTROL_MASK
        if (event.state & mod_mask and event.keyval == Gdk.KEY_f) or event.keyval == Gdk.KEY_slash:
            self.search.grab_focus()

    def on_key_pressed_on_search(self, _, event):
        if event.keyval in [Gdk.KEY_Escape, Gdk.KEY_Return]:
            # The focus of the selected item gets screwed up,
            # so we need to re-set the cursor
            selected_index = self.lookup_item_index(self.selected)
            self.select_item(selected_index)
            self.iconview.grab_focus()

    def on_search_change(self, search_entry):
        self.search_text = search_entry.get_text()
        self.filter.refilter()

    def lookup_item_index(self, name):
        return list(self.items.keys()).index(name)

    def get_item_name_by_index(self, iconview, index):
        model = iconview.get_model()
        iter = model.get_iter(Gtk.TreePath(index))
        return model.get_value(iter, self._NAME_COLUMN)

    def on_selection_changed(self, iconview):
        items = iconview.get_selected_items()
        if len(items) < 1:
            return
        self.selected = self.get_item_name_by_index(iconview, items[0].get_indices()[0])

    def on_item_activated(self, iconview, path):
        name = self.get_item_name_by_index(iconview, path.get_indices()[0])
        #self.selected = self.lookup_item_index(name)
        self.selected = name

        self.emit('item-selected', self.selected)
        self.destroy()

    def on_button_press(self, menu, event):
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return False
        if event.button != Gdk.BUTTON_SECONDARY:
            return False

        path = self.iconview.get_path_at_pos(event.x, event.y)
        if path is not None:
            self.select_item(path)

        menu.popup(None, None, None, None, event.button, event.time)
        return True

    def on_response(self, _, response):
        if response == Gtk.ResponseType.OK:
            self.emit('item-selected', self.selected)
        self.destroy()
