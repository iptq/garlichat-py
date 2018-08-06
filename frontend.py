import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Application(Gtk.Application):
    parent = None

    def __init__(self, parent, args=None, kwargs=None):
        if args is None: args = []
        if kwargs is None: kwargs = {}
        super().__init__(*args, application_id="gc.garlichat", **kwargs)
        self.parent = parent
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self, title="Garlichat", window_position=Gtk.WindowPosition.CENTER)
            self.window.set_default_size(854, 480)
            self.window.connect("destroy", self.destroy)

            v = Gtk.VBox()
            self.window.add(v)

            # menus n shit

            menubar = Gtk.MenuBar()
            v.pack_start(menubar, False, False, 2)

            main_menu = Gtk.MenuItem("Garlichat")
            menubar.append(main_menu)
            main_submenu = Gtk.Menu()
            main_menu.set_submenu(main_submenu)

            exit_item = Gtk.MenuItem("Exit")
            exit_item.connect("activate", self.destroy)
            main_submenu.append(exit_item)

            help_menu = Gtk.MenuItem("Help")
            menubar.append(help_menu)
            help_submenu = Gtk.Menu()
            help_menu.set_submenu(help_submenu)

            # the main view

            pain = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
            pain.set_position(240)
            # pain.set_resize(False)
            pain.set_wide_handle(True)
            v.pack_end(pain, True, True, 2)

            sidebar = Gtk.ListBox()
            pain.pack1(sidebar, False, False)

            sidebar2 = Gtk.ListBox()
            pain.pack2(sidebar2, True, True)

        self.window.show_all()

    def destroy(self, _):
        Gtk.main_quit()
        self.parent.quit()
        sys.exit(0)
