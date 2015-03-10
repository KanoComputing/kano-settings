#!/usr/bin/env python

# set_screensaver.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import shutil
from gi.repository import Gtk, GdkPixbuf
from kano_settings.templates import ScrolledWindowTemplate, Template
# from kano_settings.data import get_data
from kano.gtk3.buttons import OrangeButton

screensaver_path = "/usr/share/kano-settings/screensaver_icons/"


class SetScreensaver(ScrolledWindowTemplate):

    # Match the data from set_wallpaper
    NUMBER_OF_ROWS = 2
    NUMBER_OF_COLUMNS = 4
    COLUMN_PADDING = 5
    ROW_PADDING = 0
    ICON_WIDTH = 90
    ICON_HEIGHT = 90

    def __init__(self, win):
        # title = self.data["LABEL_1"]
        # description = self.data["LABEL_2"]
        # kano_label = self.data["KANO_BUTTON"]
        title = "Choose your screensaver"
        description = "You know you want to"
        kano_label = "APPLY CHANGES"

        ScrolledWindowTemplate.__init__(self, title, description, kano_label)

        self.win = win
        # self.win.set_main_widget(self)

        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.orange_button = OrangeButton('Advanced')
        self.orange_button.connect('button-release-event', self.go_to_advanced)

        self.table = Gtk.Table(
            self.NUMBER_OF_ROWS, self.NUMBER_OF_COLUMNS, True
        )
        self.table.set_row_spacings(self.ROW_PADDING)
        self.table.set_col_spacings(self.COLUMN_PADDING)
        self.buttons = {}
        self.buttons_list = []

        # List of screensavers
        self.screensavers = {}
        self.create_list_screensavers()

        # Create thumbnail images
        self.images = {}

        # Attach to table
        row = 0
        j = 0

        for button in self.buttons_list:
            self.table.attach(
                button, j, j + 1, row, row + 1,
                Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0
            )

            j = (j + 1) % self.NUMBER_OF_COLUMNS

            if j == 0:
                row += 1

        # the wallpaper thumbnails will be inside a table which we put
        # into a scrollable window
        self.sw.add_with_viewport(self.table)

        self.win.show_all()

    def go_to_advanced(self, widget, event):
        self.win.remove_main_widget()
        SetScreensaverAdvanced(self.win)

    def create_list_screensavers(self):
        # For now, we only need to return one
        self.screensavers = [
            {
                'title': 'Orange Cube',
                'program': 'test_program',
                'image': '/usr/share/kano-settings/media/screensavers'
            }
        ]

    def pack_images(self):
        for screensaver in self.screensavers:
            # Assume the screensaver items are square
            # May not need this extra pixbuf step
            image_path = screensaver['image']
            screensaver_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                image_path, 90, 90
            )
            image = Gtk.Image()
            image.set_from_pixbuf(screensaver_pixbuf)

    # Migrate these functions to common with the wallpaper?
    # e.g. migrate to system/appearence.py
    #############################################################

    def select_screensaver(self, widget=None, event=None, image_name=""):
        '''Add class to wallpaper picture which displays border even when
        mouse is moved
        '''
        for name, button in self.buttons.iteritems():
            style = button.get_style_context()
            style.remove_class("wallpaper_box_active")
            style.add_class("wallpaper_box")
        style = self.buttons[image_name].get_style_context()
        style.remove_class("wallpaper_box")
        style.add_class("wallpaper_box_active")
        self.set_selected(image_name)

    # Get the current selected wallpaper
    # Handles global variable wallpaper_array
    def get_selected(self):
        for x in self.wallpapers:
            if self.wallpapers[x]['selected']:
                return x

    # Set the currents elected wallpaper
    # Handles global variable wallpaper_array
    def set_selected(self, image_name):
        # Unselect current one
        selected = self.get_selected()
        if selected:
            self.screensaver[selected]['selected'] = False
        # Select the new one
        self.screensaver[image_name]['selected'] = True
        # Currently our screensavers aren't locked, so no need for this
        # unlocked = self.screensaver[image_name]['unlocked']

        # Enable Apply Changes button accordingly
        self.kano_button.set_sensitive(True)


# These are the values we want to change the filepaths to
# kdesk_config = '/usr/share/kano-desktop/kdesk/.kdeskrc'
# kdesk_config_backup = '/usr/share/kano-desktop/kdesk/.kdeskrc-backup'
kdesk_config = os.path.join(os.path.dirname(__file__), '..', 'test_kdeskrc')
kdesk_config_copy = os.path.join(os.path.dirname(__file__),
                                 '..', 'test_kdeskrc_copy')


class SetScreensaverAdvanced(Template):
    # get data here

    def __init__(self, win):
        title = 'Screensaver - advanced'
        description = ''
        kano_label = 'APPLY CHANGES'

        Template.__init__(self, title, description, kano_label)
        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.checkbutton = Gtk.CheckButton()
        self.checkbutton.set_label('Turn on screensaver?')
        self.checkbutton.connect('button-release-event', self.screensaver_on)
        self.scale = Gtk.Scale()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(self.checkbutton, True, True, 0)
        hbox.pack_start(self.scale, True, True, 0)

        self.box.pack_start(hbox, True, True, 0)

    def go_to_select_appearence(self):
        '''This takes you back to the menu where you can change your
        wallpaper and screensaver
        '''
        self.win.remove_main_widget()
        self.win.go_to_home()

    def read_config(self):
        '''Check the values of the slider and whetehr the screensaver is on
        Check the kdeskrc file directly
        '''

    def screensaver_on(self, button, event):
        '''This is the callback for the Turn On checkbutton
        Depending on the value of the checkbutton, this will turn on or off
        the screensaver
        '''
        is_screensaver_on = button.get_sensitive()
        self.scale.set_sensitive(is_screensaver_on)

    def turn_off_screensaver(self):
        '''Set the timeout of the screensaver to 0,
        set the scale value to 1 and disable the scale
        '''
        self.set_kdesk_config('ScreenSaverTimeout', 0)

    def turn_on_screensaver(self):
        '''Set the timeout of the screensaver to the value of the scale
        '''
        timeout = self.scale.get_value_pos()
        self.set_kdesk_config('ScreenSaverTimeout', timeout)

    def apply_changes(self):
        '''All the modifications the user makes to the screensaver
        will take place on the kdesk_copy.  if they click Apply Changes,
        this will copy the copy onto the original file
        '''
        shutil.move(kdesk_config_copy, kdesk_config)

    def set_kdesk_config(self, param_name, param_value):
        '''Given a param name and a param value, will set the kdesk_config
        accordingly
        '''
        f = open(kdesk_config, 'r')

        # Need the setting which wipes the original file clean
        g = open(kdesk_config_copy, 'w+')

        for line in f:
            if line in param_name:
                line = line.split(':')[0] + ' ' + param_value
            g.write(line)

    def get_kdesk_config(self, param_name):
        '''For a particular parameter, get the config value
        This will always return a string.
        '''
        f = open(kdesk_config, 'w')

        for line in f:
            if line in param_name:
                param_value = line.split(':')[1].strip()
                return param_value
