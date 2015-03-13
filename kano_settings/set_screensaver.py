#!/usr/bin/env python

# set_screensaver.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk, GdkPixbuf
from kano_settings.templates import Template, ScrolledWindowTemplate
from kano_settings.image_table import ImageTable
import os
import sys

dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if __name__ == '__main__' and __package__ is None:
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)


from kano_settings.system.screensaver import (
    is_screensaver_on, get_screensaver_timeout, set_screensaver_timeout,
    set_screensaver_program
)

screensaver_path = "/usr/share/kano-settings/media/ScreensaverIcons"


class SetScreensaver(ScrolledWindowTemplate):

    def __init__(self, win):
        ScrolledWindowTemplate.__init__(
            self,
            'Change your screensaver',
            '',
            'CHANGE SCREENSAVER',
            'Advanced Options'
        )

        self.win = win

        self.table = ScreensaverTable()
        self.orange_button.connect('button-release-event', self.go_to_advanced)

        # The image thumbnails will be inside a table which we put
        # into a scrollable window
        self.sw.add_with_viewport(self.table)
        self.adjust_size_of_sw()

        # Disable the Kano Button until they select a valid wallpaper
        self.kano_button.set_sensitive(False)
        self.table.connect('image_selected', self.enable_kano_button)
        self.kano_button.connect('button-release-event', self.apply_changes)

    def go_to_advanced(self, widget=None, event=None):
        self.win.remove_main_widget()
        SetScreensaverAdvanced(self.win)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # Change program name in the kdesk config to change to the program
            # name in the dictionary
            name = self.table.get_selected()
            program = self.table.images[name]['program']
            set_screensaver_program(program)
            self.table.unselect_all()
            self.kano_button.set_sensitive(False)

    def adjust_size_of_sw(self):
        '''Make scrolled window tall enough to show a full number of rows and
        columns, plus all the green highlighting around the selected item
        '''

        height = (
            self.table.number_of_rows * (20 + self.table.icon_height) +
            (self.table.number_of_rows + 2) * (self.table.row_padding)
        )
        self.sw.set_size_request(-1, height)

    def enable_kano_button(self, widget=None, event=None):
        selected = self.table.get_selected()
        self.kano_button.set_sensitive(selected is not None)


class ScreensaverTable(ImageTable):
    icon_width = 90
    icon_height = 90
    row_padding = 0
    column_padding = 5

    number_of_rows = 2
    number_of_columns = 4

    def __init__(self):
        ImageTable.__init__(
            self, self.number_of_rows, self.number_of_columns,
            self.row_padding, self.column_padding,
            self.icon_width, self.icon_height
        )

        self.create_image_dict()
        self.create_button_list()

        # Pack the button list into the table
        self.attach_buttons_to_table(self.button_list)

    def create_image_dict(self):
        '''Creates the member variable self.images with a structure of the form
        {
            name: {
                'program': '/usr/bin/kdesk-eglsaver',
                'path': path,
                'selected': False,
                'unlocked': True
            }
        }
        '''

        self.images = {}

        # Currently we only return one screensaver
        self.images['orange-cube'] = {
            'program': '/usr/bin/kdesk-eglsaver',
            'path': '/usr/share/kano-settings/media/orange-cube.png',
            'selected': True,
            'unlocked': True
        }

    def create_button_list(self):
        '''Decide on an order for the items in the table
        '''

        self.button_list = []

        for item_name, item_dict in self.images.iteritems():
            image = self.format_image(item_name)
            button = self.create_button(item_name, image)
            self.button_list.append(button)
            self.images[item_name]['button'] = button

    def format_image(self, image_name):
        '''Return an Gtk.Image self.icon_width by self.icon_height
        '''

        path = self.images[image_name]['path']
        image = Gtk.Image.new_from_file(path)
        return image


class SetScreensaverAdvanced(Template):

    def __init__(self, win):
        title = 'Screensaver - advanced'
        description = ''
        kano_label = 'APPLY CHANGES'

        Template.__init__(self, title, description, kano_label)
        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.go_to_set_appearance)

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)

        # Want a label to the left, so we need to pack it separately
        checkbutton_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=35
        )
        self.checkbutton = Gtk.CheckButton()
        label = Gtk.Label('Turn on screensaver')
        label.get_style_context().add_class('checkbutton_label')
        checkbutton_box.pack_start(label, False, False, 0)
        checkbutton_box.pack_start(self.checkbutton, False, False, 0)

        self.checkbutton.connect('toggled', self.enable_screensaver_scale)

        scalebox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        label = Gtk.Label("Length of time before \nscreensaver launches")
        label.get_style_context().add_class('checkbutton_label')
        label.set_margin_top(25)
        self.scale = Gtk.Scale.new_with_range(
            orientation=Gtk.Orientation.HORIZONTAL,
            min=1,
            max=1000,
            step=1
        )
        self.scale.set_size_request(300, 1)

        scalebox.pack_start(label, False, False, 0)
        scalebox.pack_start(self.scale, False, False, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(checkbutton_box, True, True, 0)
        vbox.pack_start(scalebox, True, True, 0)
        vbox.set_margin_top(20)

        self.box.pack_start(vbox, True, True, 0)
        self.scale.set_sensitive(False)

        self.show_config_on_loading_page()

        self.win.show_all()

    def enable_screensaver_scale(self, button):
        '''This is the callback for the Turn On checkbutton
        Depending on the value of the checkbutton, this will turn on or off
        the screensaver and disable the Gtk.Scale
        '''
        check_screensaver = button.get_active()
        self.scale.set_sensitive(check_screensaver)

    def apply_changes(self, widget=None, event=None):
        '''Get all the modifications and modify the .kdeskrc file
        '''
        if self.checkbutton.get_active():
            scale_value = int(self.scale.get_value())
            set_screensaver_timeout(scale_value)
        else:
            # This turns off the screensaver
            set_screensaver_timeout('0')

        self.go_to_set_appearance()

    def go_to_set_appearance(self, widget=None, event=None):
        '''Go to the Set Appearance screen
        '''
        self.win.remove_main_widget()
        from kano_settings.set_appearance import SetAppearance
        SetAppearance(self.win)

    def show_config_on_loading_page(self):
        '''Makes the relevent widgets sensitive depending on the kdesk
        config
        '''
        screensaver_on = is_screensaver_on()
        self.checkbutton.set_active(screensaver_on)

        if screensaver_on:
            value = int(get_screensaver_timeout())
            self.scale.set_value(value)
