#!/usr/bin/env python

# set_wallpaper.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk, GdkPixbuf
from kano_settings.templates import ScrolledWindowTemplate
from kano_settings.config_file import username

wallpaper_path = "/usr/share/kano-desktop/wallpapers/"
kano_draw_path = os.path.join('/home', username, 'Draw-content/wallpapers/')
padlock_path = "/usr/share/kano-settings/media/Icons/padlock.png"  # needs to be 95x95
name_pattern = "-4-3.png"


class SetImage(ScrolledWindowTemplate):
    '''This class is for any screen which has the option to select multiple
    items
    '''

    def __init__(self, win, title, description, kano_label,
                 orange_button_text=None):

        self.icon_width = 90
        self.icon_height = 90
        self.row_padding = 0
        self.column_padding = 5

        self.number_of_rows = 2
        self.number_of_columns = 4

        ScrolledWindowTemplate.__init__(
            self,
            title,
            description,
            kano_label,
            orange_button_text
        )

        self.win = win

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)
        self.kano_button.set_margin(10, 0, 20, 0)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.images = {}
        self.buttons_list = []

    def setup_table(self):
        '''Initialise table with the number of rows and columns needed
        '''

        self.table = Gtk.Table(self.number_of_rows, self.number_of_columns,
                               True)
        self.table.set_row_spacings(self.row_padding)
        self.table.set_col_spacings(self.column_padding)

    def attach_buttons_to_table(self):
        '''Pack the buttons in the table
        '''

        # Attach to table
        row = 0
        j = 0

        for button in self.buttons_list:
            self.table.attach(button, j, j + 1, row, row + 1,
                              Gtk.AttachOptions.EXPAND,
                              Gtk.AttachOptions.EXPAND, 0, 0)

            j = (j + 1) % self.number_of_columns
            if j == 0:
                row += 1

    def adject_height_of_scrolled_window(self):
        # Make scrolled window tall enough to show a full number of rows and
        # columns, plus all the green highlighting around the selected item
        height = (self.number_of_rows * (20 + self.icon_height) +
                  (self.number_of_rows + 2) * (self.row_padding))
        self.sw.set_size_request(-1, height)

    def add_selected_css_class(self, image_name=""):
        '''Adds the css class that shows the image that has been selected,
        even when the mouse is moved away
        '''

        for img_name, img_dict in self.images.iteritems():
            for name, prop in img_dict.iteritems():
                if name == 'button':
                    style = prop.get_style_context()
                    style.remove_class("wallpaper_box_active")
                    style.add_class("wallpaper_box")

        style = self.images[image_name]['button'].get_style_context()
        style.remove_class("wallpaper_box")
        style.add_class("wallpaper_box_active")

    def select_image_cb(self, widget, event, image_name):
        self.add_selected_css_class(image_name)
        self.set_selected(image_name)

    def add_to_button_list(self, name, unlocked=True):
        '''Creates a button from the image and adds to the
        button_list so we can keep track of the order
        '''
        image = self.format_image(name)
        button = self.create_button(name, image, unlocked)
        self.images[name]['button'] = button

        # so we keep the order of the buttons
        self.buttons_list.append(button)

    def format_image(self, name):
        '''This returns a Gtk.Image size 90 by 90 pixels
        This depends on the original image that we're processing,
        so is changed on inheritance
        '''
        pass

    def create_button(self, name, image, unlocked=True):
        '''This places the images onto a Gtk.Button and adds the highlighting
        Returns the button
        '''

        # Create the container for the thumbnails
        container = Gtk.Fixed()
        container.put(image, 0, 0)

        # Add the padlock overlay on the thumbnail if it is locked
        if not unlocked:
            # Recreate padlock overlay here becuase otherwise it's parent gets
            # set by the class
            padlock_pixbuf = GdkPixbuf.Pixbuf.new_from_file(padlock_path)
            padlock_overlay = Gtk.Image()
            padlock_overlay.set_from_pixbuf(padlock_pixbuf)
            container.put(padlock_overlay, 0, 0)

        button = Gtk.Button()
        button.get_style_context().add_class('wallpaper_box')
        button.add(container)
        image.set_padding(3, 3)
        button.connect('button_press_event', self.select_image_cb,
                       name)
        return button

    def set_selected(self, image_name):
        '''Added the selected CSS class to the item.
        '''

        # Unselect current one
        selected = self.get_selected()
        if selected:
            self.images[selected]['selected'] = False

        # Select the new one
        self.images[image_name]['selected'] = True

    def get_selected(self):
        '''Get the current selected wallpaper
        '''
        for x in self.images:
            if self.images[x]['selected']:
                return x

    def adjust_size_of_sw(self):
        '''Make scrolled window tall enough to show a full number of rows and
        columns, plus all the green highlighting around the selected item
        '''

        height = (
            self.number_of_rows * (20 + self.icon_height) +
            (self.number_of_rows + 2) * (self.row_padding)
        )
        self.sw.set_size_request(-1, height)
