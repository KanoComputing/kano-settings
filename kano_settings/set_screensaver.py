#!/usr/bin/env python

# set_screensaver.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk
from kano_settings.templates import Template
from kano_settings.set_image import SetImage
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


class SetScreensaver(SetImage):
    def __init__(self, win):
        SetImage.__init__(self, win, 'Choose your screensaver',
                          '', 'APPLY CHANGES', 'Advanced Settings')
        self.create_screensaver_list()
        self.setup_table()
        self.attach_buttons_to_table()

        self.orange_button.connect('button-release-event', self.go_to_advanced)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.table, False, False, 0)
        self.sw.add_with_viewport(vbox)
        self.adjust_size_of_sw()

    def create_screensaver_list(self):
        '''Return list of screensavers of the form
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

        self.add_to_button_list('orange-cube')

    def format_image(self, name):
        image_path = self.images[name]['path']
        image = Gtk.Image.new_from_file(image_path)
        return image

    def go_to_advanced(self, widget=None, event=None):
        self.win.remove_main_widget()
        SetScreensaverAdvanced(self.win)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # Change program name in the kdesk config to change to the program
            # name in the dictionary
            name = self.get_selected()
            program = self.images[name]['program']
            set_screensaver_program(program)

            # Go to home screen
            self.win.go_to_home()


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
        # self.scale = Gtk.Scale()

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

        self.win.show_all()

    def go_to_select_appearence(self):
        '''This takes you back to the menu where you can change your
        wallpaper and screensaver
        '''
        self.win.remove_main_widget()
        self.win.go_to_home()

    def enable_screensaver_scale(self, button):
        '''This is the callback for the Turn On checkbutton
        Depending on the value of the checkbutton, this will turn on or off
        the screensaver
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

        self.win.go_to_home()

    def show_config_on_loading_page(self):
        '''Makes the relevent widgets sensitive depending on the kdesk
        config
        '''
        screensaver_on = is_screensaver_on()
        self.checkbutton.set_active(screensaver_on)

        if screensaver_on:
            value = get_screensaver_timeout()
            self.scale.set_value(value)
