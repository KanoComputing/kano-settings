#!/usr/bin/env python

# set_wallpaper.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gdk
import os
from gi.repository import Gtk, GdkPixbuf
from .config_file import get_setting, set_setting
from kano_profile.badges import calculate_badges
from kano_settings.config_file import username
from kano_settings.system.wallpaper import change_wallpaper
from kano_settings.set_image import SetImage

wallpaper_path = "/usr/share/kano-desktop/wallpapers/"
kano_draw_path = os.path.join('/home', username, 'Draw-content/wallpapers/')
padlock_path = "/usr/share/kano-settings/media/Icons/padlock.png"  # needs to be 95x95
name_pattern = "-4-3.png"


class SetWallpaper(SetImage):

    def __init__(self, win):
        SetImage.__init__(
            self, win, "Choose your background", "", "APPLY CHANGES"
        )
        self.create_wallpaper_list()
        self.setup_table()
        self.order_packing_of_wallpapers()
        self.attach_buttons_to_table()

        # The image thumbnails will be inside a table which we put
        # into a scrollable window
        self.sw.add_with_viewport(self.table)
        self.adjust_size_of_sw()

    def create_wallpaper_list(self):
        '''Get the wallpapers from the profile, the Kano Draw pictures
        and find which ones are unlocked
        '''

        self.get_wallpapers(wallpaper_path)
        self.get_wallpapers(kano_draw_path)

        # To get info about which environments are unlocked we first calculate
        # badges then we take the 'achieved' attribute of an environment and
        # add it to the attribute of our local list of wallpapers
        #
        #   NOTE: it relies on the wallpapers in kano-desktop to me named as
        #   their respective rule in kano-profile with the following pattern:
        #
        #         [rule_name]-background[name_pattern]
        #         e.g. [arcade_hall]-background[-4-3.png]
        environments = calculate_badges()['environments']['all']
        for environment, attributes in environments.iteritems():
            try:
                self.images[environment]['unlocked'] = attributes['achieved']
            except:
                pass

    def get_wallpapers(self, path):
        '''Find the list of wallpaper files
        Go through the paths of the wallpapers and stuff them in the
        dictionary
        '''

        if os.path.exists(path):
            for file in os.listdir(path):
                if name_pattern in file:
                    self.images[file[:-8]] = {
                        'path': path,
                        'selected': False,
                        'unlocked': True
                    }

    def order_packing_of_wallpapers(self):
        '''Fix the order of the packing of the wallpapers
        '''

        # In turn, add the default, unlocked, and finally locked wallpapers
        # using a separate list to account for ordering
        for name, attributes in self.images.iteritems():
            if 'background' in name:
                self.add_to_button_list(name, True)

        for name, attributes in self.images.iteritems():
            if attributes['unlocked'] and 'background' not in name:
                self.add_to_button_list(name, True)

        for name, attributes in self.images.iteritems():
            if not attributes['unlocked']:
                self.add_to_button_list(name, False)

    def read_config(self):
        return get_setting("Wallpaper")

    def format_image(self, name):
        '''In the wallpaper, we get a 4 by 3 ratio, so need to change the size
        to 120 by 90 and then crop it
        '''
        width = self.icon_width
        height = self.icon_height

        # Create the wallpaper thumbnail
        try:
            # The original picture is not square, so resize the picture to
            # scale and then crop the picture
            wallpaper_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                self.get_path(name) + name + name_pattern, 120, 90
            )
            cropped_wallpaper = wallpaper_pixbuf.new_subpixbuf(15, 0, width,
                                                               height)
            image = Gtk.Image()
            image.set_from_pixbuf(cropped_wallpaper)
            return image
        except:
            return None

    def get_path(self, name):
        return self.images[name]['path']

    def update_config(self):
        # Add new configurations to config file.
        selected = self.get_selected()
        if selected:
            set_setting("Wallpaper", selected)

    def apply_changes(self, button, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            image_name = self.get_selected()
            path = self.get_path(image_name)
            change_wallpaper(path, image_name)
            self.update_config()
            self.win.go_to_home()
