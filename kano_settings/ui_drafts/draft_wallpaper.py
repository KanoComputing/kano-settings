#!/usr/bin/env python

# set_wallpaper.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, GdkPixbuf
import kano_settings.config_file as config_file
#import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano_settings.constants as constants
import os

selected_button = 0
initial_button = 0
NUMBER_OF_COLUMNS = 5
# Calculate this dynamically once we have data about pictures
NUMBER_OF_ROWS = 2
COLUMN_PADDING = 0
ROW_PADDING = 0
ICON_WIDTH = 90
ICON_HEIGHT = 90

wallpaper_path = "/usr/share/kano-desktop/wallpapers/"


def activate(_win, box, update):
    global selected_button, initial_button

    wallpaper_array = ["Icon-Audio", "Icon-Display", "Icon-Overclocking", "Icon-Keyboard", "Icon-Email", "Icon-Mouse", "Icon-Wallpaper", "Icon-Account"]

    title = Gtk.Label("Choose your background")
    title.get_style_context().add_class('title')
    images = []
    boxes = []

    wallpaper_table = Gtk.Table(NUMBER_OF_ROWS, NUMBER_OF_COLUMNS, True)
    wallpaper_table.set_row_spacings(ROW_PADDING)
    wallpaper_table.set_col_spacings(COLUMN_PADDING)

    for i in range(len(wallpaper_array)):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(constants.media + "/Icons/" + wallpaper_array[i] + ".png", ICON_WIDTH, ICON_HEIGHT)
        image = Gtk.Image()
        image.get_style_context().add_class('wallpaper_box')
        image.set_from_pixbuf(pixbuf)
        images.append(image)
        backgroundbox = Gtk.Button()
        backgroundbox.add(image)
        backgroundbox.connect('button_press_event', select_wallpaper, images, image)
        #backgroundbox.get_style_context().add_class('background_box')
        boxes.append(backgroundbox)

    settings = fixed_size_box.Fixed()

    # Attach to table
    index = 0
    row = 0

    while index < len(wallpaper_array):
        for j in range(NUMBER_OF_COLUMNS):
            if index < len(wallpaper_array):
                wallpaper_table.attach(boxes[index], j, j + 1, row, row + 1,
                                       Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                index += 1
            else:
                grey_box = Gtk.Button()
                grey_box.set_size_request(ICON_WIDTH, ICON_HEIGHT)
                grey_box.get_style_context().add_class('grey_box')
                grey_box.connect('button_press_event', add_wallpaper, wallpaper_array)
                wallpaper_table.attach(grey_box, j, j + 1, row, row + 1,
                                       Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                index += 1
        row += 1

    settings.box.pack_start(wallpaper_table, False, False, 10)

    # Add apply changes button under the main settings content
    box.pack_start(title, False, False, 0)
    box.pack_start(settings.box, False, False, 0)
    box.pack_start(update.box, False, False, 0)
    update.enable()


# Add class to wallpaper picture which displays border even when mouse is moved
def select_wallpaper(widget=None, event=None, images=None, image=None):

    for x in images:
        style = x.get_style_context()
        style.remove_class("wallpaper_box_active")
        style.add_class("wallpaper_box")

    image_style = image.get_style_context()
    image_style.remove_class("wallpaper_box")
    image_style.add_class("wallpaper_box_active")


# Add new wallpaper option to grey box
def add_wallpaper(widget=None, event=None, wallpaper_array=None):
    print "grey_box"


def apply_changes(button):

    #  Mode   speed
    # Slow     1
    # Normal  default
    # High     10

    # Mode has no changed
    if initial_button == selected_button:
        return

    config = "Slow"
    # Slow configuration
    if selected_button == 0:
        config = "Slow"
    # Modest configuration
    elif selected_button == 1:
        config = "Normal"
    # Medium configuration
    elif selected_button == 2:
        config = "Fast"

    # Update config
    config_file.replace_setting("Mouse", config)


def change_wallpaper(image_name):
    # home directory
    USER = os.environ['SUDO_USER']
    deskrc_path = "/home/%s/.kdeskrc" % (USER)
    if not os.path.isfile(deskrc_path):
        return 1

     # Change wallpaper in deskrc
    image_169 = "%s%s-16-9.png" % (wallpaper_path, image_name)
    image_43 = "%s%s-4-3.png" % (wallpaper_path, image_name)
    image_1024 = "%s%s-1024.png" % (wallpaper_path, image_name)
    # Read deskrc config file
    f = file(deskrc_path)
    newlines = []
    for line in f:
        if "Background.File-medium: " in line:
            line = "  Background.File-medium: %s\n" % (image_1024)
        if "Background.File-4-3: " in line:
            line = "  Background.File-4-3: %s\n" % (image_43)
        if "Background.File-16-9: " in line:
            line = "  Background.File-16-9: %s\n" % (image_169)
        newlines.append(line)
    # Overwrite config file with new lines
    outfile = file(deskrc_path, 'w')
    outfile.writelines(newlines)

    # Refresh the wallpaper
    os.system('pkill kdesk && kdesk &')
    # TODO: can we use ksdek -w for previewing the wallpaper?

    return 0
