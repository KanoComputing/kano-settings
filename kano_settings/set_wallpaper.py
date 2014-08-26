#!/usr/bin/env python

# set_wallpaper.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gdk
import os
from gi.repository import Gtk, GdkPixbuf
from kano_settings.templates import ScrolledWindowTemplate
from .config_file import get_setting, set_setting
from kano_profile.badges import calculate_badges
from kano_settings.data import get_data
from kano_settings.system.wallpaper import change_wallpaper

wallpaper_path = "/usr/share/kano-desktop/wallpapers/"
padlock_path = "/usr/share/kano-settings/media/Icons/padlock.png"  # needs to be 95x95
kdeskrc_default = "/usr/share/kano-desktop/kdesk/.kdeskrc"
kdeskrc_home = "/home/%s/.kdeskrc"
name_pattern = "-4-3.png"


class SetWallpaper(ScrolledWindowTemplate):
    data = get_data("SET_WALLPAPER")

    def __init__(self, win):
        title = self.data["LABEL_1"]
        description = self.data["LABEL_2"]
        kano_label = self.data["KANO_BUTTON"]

        ScrolledWindowTemplate.__init__(self, title, description, kano_label)

        NUMBER_OF_ROWS = 2
        NUMBER_OF_COLUMNS = 4
        COLUMN_PADDING = 5
        ROW_PADDING = 0
        ICON_WIDTH = 90
        ICON_HEIGHT = 90

        self.win = win
        self.win.set_main_widget(self)

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)
        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.table = Gtk.Table(NUMBER_OF_ROWS, NUMBER_OF_COLUMNS, True)
        self.table.set_row_spacings(ROW_PADDING)
        self.table.set_col_spacings(COLUMN_PADDING)
        self.buttons = {}
        self.buttons_list = []

        # List of wallpapers
        self.wallpapers = {}
        self.create_list_wallpaper()

        # Create thumbnail images
        self.images = {}

        # in turn, add the default, unlocked, and finally locked wallpapers
        # using a separate list to account for ordering
        for name, attributes in self.wallpapers.iteritems():
            if 'background' in name:
                self.add_wallpaper_to_table(name, ICON_WIDTH, ICON_HEIGHT, True)

        for name, attributes in self.wallpapers.iteritems():
            if attributes['unlocked'] and 'background' not in name:
                self.add_wallpaper_to_table(name, ICON_WIDTH, ICON_HEIGHT, True)

        for name, attributes in self.wallpapers.iteritems():
            if not attributes['unlocked']:
                self.add_wallpaper_to_table(name, ICON_WIDTH, ICON_HEIGHT, False)

        # Attach to table
        row = 0
        j = 0

        for button in self.buttons_list:
            self.table.attach(button, j, j + 1, row, row + 1,
                              Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)

            j = (j + 1) % NUMBER_OF_COLUMNS
            if j == 0:
                row += 1

        # the wallpaper thumbnails will be inside a table which we put
        # into a scrollable window
        self.sw.add_with_viewport(self.table)

        self.win.show_all()

    def add_wallpaper_to_table(self, name, width, height, unlocked):
        # recreate padlock overlay here becuase otherwise it's parent gets set by the class
        padlock_pixbuf = GdkPixbuf.Pixbuf.new_from_file(padlock_path)
        padlock_overlay = Gtk.Image()
        padlock_overlay.set_from_pixbuf(padlock_pixbuf)

        # create the wallpaper thumbnail
        wallpaper_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(wallpaper_path + name + name_pattern, 120, 90)
        cropped_wallpaper = wallpaper_pixbuf.new_subpixbuf(15, 0, width, height)
        image = Gtk.Image()
        image.set_from_pixbuf(cropped_wallpaper)

        # create the container for the thumbnails
        container = Gtk.Fixed()
        container.put(image, 0, 0)

        # add the padlock overlay on the thumbnail if it is locked
        if not unlocked:
            container.put(padlock_overlay, 0, 0)

        self.images[name] = image
        backgroundbox = Gtk.Button()
        backgroundbox.get_style_context().add_class('wallpaper_box')
        backgroundbox.add(container)
        image.set_padding(3, 3)
        backgroundbox.connect('button_press_event', self.select_wallpaper, name)
        self.buttons[name] = backgroundbox
        self.buttons_list.append(backgroundbox)

    # Add class to wallpaper picture which displays border even when mouse is moved
    def select_wallpaper(self, widget=None, event=None, image_name=""):
        for name, button in self.buttons.iteritems():
            style = button.get_style_context()
            style.remove_class("wallpaper_box_active")
            style.add_class("wallpaper_box")
        style = self.buttons[image_name].get_style_context()
        style.remove_class("wallpaper_box")
        style.add_class("wallpaper_box_active")
        self.set_selected(image_name)

    def add_wallpaper(self, widget=None, event=None):
        pass

    # Get the current selected wallpaper
    # Handles global variable wallpaper_array
    def get_selected(self):
        for x in self.wallpapers:
            if self.wallpapers[x]['selected']:
                return x

    # Set the currents elected wallpaper
    # Handles global variable wallpaper_array
    def set_selected(self, image_name):
        for x in self.wallpapers:
            self.wallpapers[x]['selected'] = False

        if self.wallpapers[image_name]['unlocked']:
            self.wallpapers[image_name]['selected'] = True
            self.kano_button.set_sensitive(True)
        else:
            self.kano_button.set_sensitive(False)

    def read_config(self):
        return get_setting("Wallpaper")

    def update_config(self):
        # Add new configurations to config file.
        selected = self.get_selected()
        if selected:
            set_setting("Wallpaper", selected)

    def create_list_wallpaper(self):
        self.get_wallpapers()

        # To get info about which environments are unlocked we first calculate badges
        # then we take the 'achieved' attribute of an environment and add it to
        # the attribute of our local list of wallpapers
        #
        #   NOTE: it realies on the wallpapers in kano-desktop to me named as their
        #         respective rule in kano-profile with the following pattern:
        #
        #         [rule_name]-background[name_pattern]
        #         e.g. [arcade_hall]-background[-4-3.png]
        environments = calculate_badges()['environments']['all']
        for environment, attributes in environments.iteritems():
            try:
                self.wallpapers[environment]['unlocked'] = attributes['achieved']
            except:
                pass

    def get_wallpapers(self):
        if not os.path.exists(wallpaper_path):
            return
        for file in os.listdir(wallpaper_path):
            if name_pattern in file:
                self.wallpapers[file[:-8]] = {
                    'selected': False,
                    'unlocked': True
                }

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            image_name = self.get_selected()
            change_wallpaper(wallpaper_path, image_name)
            self.update_config()
            self.win.go_to_home()
