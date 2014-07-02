#!/usr/bin/env python

# set_wallpaper.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk, GdkPixbuf
import kano_settings.components.fixed_size_box as fixed_size_box
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.logging import logger
from .config_file import get_setting, set_setting

from kano_profile.badges import calculate_badges


wallpaper_path = "/usr/share/kano-desktop/wallpapers/"
kdeskrc_default = "/usr/share/kano-desktop/kdesk/.kdeskrc"
kdeskrc_home = "/home/%s/.kdeskrc"
name_pattern = "-4-3.png"


class Wallpaper():

    def __init__(self):
        NUMBER_OF_ROWS = 2
        NUMBER_OF_COLUMNS = 4
        COLUMN_PADDING = 5
        ROW_PADDING = 0
        ICON_WIDTH = 90
        ICON_HEIGHT = 90

        self.table = Gtk.Table(NUMBER_OF_ROWS, NUMBER_OF_COLUMNS, True)
        self.table.set_row_spacings(ROW_PADDING)
        self.table.set_col_spacings(COLUMN_PADDING)
        self.buttons = {}
        # List of wallpapers
        self.wallpapers = {}
        locked, unlocked = self.create_list_wallpaper()
        # Create thumbnail images
        self.images = {}
        for name in unlocked:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(wallpaper_path + name + name_pattern, 120, 90)
            cropped_pixbuf = pixbuf.new_subpixbuf(15, 0, ICON_WIDTH, ICON_HEIGHT)
            image = Gtk.Image()
            image.set_from_pixbuf(cropped_pixbuf)
            self.images[name] = image
            backgroundbox = Gtk.Button()
            backgroundbox.get_style_context().add_class('wallpaper_box')
            backgroundbox.add(image)
            image.set_padding(3, 3)
            backgroundbox.connect('button_press_event', self.select_wallpaper, name)
            self.buttons[name] = backgroundbox

        # Attach to table
        row = 0
        j = 0

        for name, button in self.buttons.iteritems():
            self.table.attach(button, j, j + 1, row, row + 1,
                              Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)

            j = (j + 1) % NUMBER_OF_COLUMNS
            if j == 0:
                row += 1

        self.scrolled_window = ScrolledWindow()
        self.scrolled_window.add_with_viewport(self.table)
        self.scrolled_window.set_size_request(520, 220)

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

        self.wallpapers[image_name]['selected'] = True

    def change_wallpaper(self):
        image_name = self.get_selected()

        logger.info('set_wallpaper / change_wallpaper image_name:{}'.format(image_name))

        # home directory
        USER = os.environ['SUDO_USER']
        deskrc_path = kdeskrc_home % (USER)
        # Wallpaper selected
        image_169 = "%s%s-16-9.png" % (wallpaper_path, image_name)
        image_43 = "%s%s-4-3.png" % (wallpaper_path, image_name)
        image_1024 = "%s%s-1024.png" % (wallpaper_path, image_name)
        # Look for the strings
        found = False
        if os.path.isfile(deskrc_path):
            f = open(deskrc_path, 'r')
            newlines = []
            for line in f:
                if "Background.File-medium:" in line:
                    line = "  Background.File-medium: %s\n" % (image_1024)
                    found = True
                elif "Background.File-4-3:" in line:
                    line = "  Background.File-4-3: %s\n" % (image_43)
                elif "Background.File-16-9:" in line:
                    line = "  Background.File-16-9: %s\n" % (image_169)
                newlines.append(line)
            f.close()
        if found:
            # Overwrite config file with new lines
            outfile = open(deskrc_path, 'w')
            outfile.writelines(newlines)
            outfile.close()
        # If not found add it
        else:
            with open(deskrc_path, "a") as outfile:
                outfile.write("  Background.File-medium: %s\n" % (image_1024))
                outfile.write("  Background.File-4-3: %s\n" % (image_43))
                outfile.write("  Background.File-16-9: %s\n" % (image_169))
        # Refresh the wallpaper
        cmd = 'sudo -u %s kdesk -w' % USER
        os.system(cmd)
        return 0

    def read_config(self):
        return get_setting("Wallpaper")

    def update_config(self):
        # Add new configurations to config file.
        selected = self.get_selected()
        if selected:
            set_setting("Wallpaper", selected)

    def create_list_wallpaper(self):
        self.get_wallpapers()

        environments = calculate_badges()['environments']['all']
        for environment, attributes in environments.iteritems():
            self.wallpapers[environment + '-background']['unlocked'] = attributes['achieved']

        locked = []
        unlocked = []
        for wallpaper, attributes in self.wallpapers.iteritems():
            if attributes['unlocked']:
                unlocked.append(wallpaper)
            else:
                locked.append(wallpaper)

        return locked, unlocked

    def get_wallpapers(self):
        if not os.path.exists(wallpaper_path):
            return
        for file in os.listdir(wallpaper_path):
            if name_pattern in file:
                self.wallpapers[file[:-8]] = {
                    'selected': False,
                    'unlocked': True
                }

wallpaper = None


def activate(_win, box, button):
    global wallpaper

    title = Gtk.Label("Choose your background")
    title.get_style_context().add_class('title')

    wallpaper = Wallpaper()
    settings = fixed_size_box.Fixed()
    settings.box.pack_start(wallpaper.scrolled_window, False, False, 10)

    # Add apply changes button under the main settings content
    box.pack_start(title, False, False, 0)
    box.pack_start(settings.box, False, False, 0)
    box.pack_start(button.align, False, False, 0)
    button.set_sensitive(True)

    _win.show_all()


def apply_changes(button):
    global wallpaper

    wallpaper.change_wallpaper()
    wallpaper.update_config()
