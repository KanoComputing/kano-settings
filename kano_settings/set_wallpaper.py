#
# set_wallpaper.py
#
# Copyright (C) 2014 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#

import os

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf, Gdk
from kano_settings.config_file import set_setting, get_setting
from kano_profile.badges import calculate_badges
from kano_settings.config_file import username
from kano_settings.system.wallpaper import change_wallpaper
from kano_settings.image_table import ImageTable
from kano_settings.templates import TwoButtonTemplate
from kano_content.api import ContentManager

wallpaper_path = "/usr/share/kano-desktop/wallpapers/"
kano_draw_path = os.path.join('/home', username, 'Draw-content/wallpapers/')
padlock_path = "/usr/share/kano-settings/media/Icons/padlock.png"  # needs to be 95x95
name_pattern = "-4-3.png"


class SetWallpaper(TwoButtonTemplate):
    def __init__(self, win, header=_("Choose a background"),
                 subheader="", buttons_shown=1):
        # This simply is a Gtk.Box with a heading, scrolledwindow and green
        # kano button and optionally an orange link
        TwoButtonTemplate.__init__(self, header, subheader, _("TRY"), _("CHOOSE"), buttons_shown)

        self.win = win
        self.get_style_context().add_class('notebook_page')

        # This isn't that neccessary for this screen, but is useful for the
        # the first screen
        self.left_button.set_sensitive(False)
        self.left_button.set_margin(10, 0, 20, 0)
        self.left_button.connect('button-release-event', self.set_wallpaper)

        self.right_button.set_margin(10, 0, 20, 0)
        self.right_button.set_sensitive(False)
        self.right_button.connect('button-release-event', self.apply_changes)

        # Initialise table
        self.table = WallpaperTable()

        # Add table to the scrolled window
        self.sw.add_with_viewport(self.table)
        self.adjust_size_of_sw()

        self.table.connect('image_selected', self.enable_kano_buttons)

    def adjust_size_of_sw(self):
        '''Make scrolled window tall enough to show a full number of rows and
        columns, plus all the green highlighting around the selected item
        '''

        height = (
            self.table.number_of_rows * (20 + self.table.icon_height) +
            (self.table.number_of_rows + 2) * (self.table.row_padding)
        )
        self.sw.set_size_request(-1, height)

    # This is the callback linked to the right button
    def apply_changes(self, button, event):
        self.set_wallpaper(button, event)

        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            self.update_config()
            self.table.unselect_all()
            self.right_button.set_sensitive(False)

    # This is the callback linked to the left button
    def set_wallpaper(self, button, event):
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:
            image_name = self.get_selected()
            self.set_wallpaper_by_image_name(image_name)
            self.left_button.set_sensitive(False)

    def reset_wallpaper(self):
        image_name = get_setting('Wallpaper')
        self.set_wallpaper_by_image_name(image_name)

    def set_wallpaper_by_image_name(self, image_name):
        path = self.table.get_path(image_name)
        change_wallpaper(path, image_name)

    def update_config(self):
        '''Add new configurations to config file.
        '''
        selected = self.get_selected()
        if selected:
            set_setting('Wallpaper', selected)

    def set_selected(self, image_name):
        '''Sets the selected element in the dictionary to True,
        and sets all the others to False
        '''

        self.table.set_selected(image_name)

    def get_selected(self):
        '''Gets the current selected wallpaper
        '''

        return self.table.get_selected()

    def enable_kano_buttons(self, widget=None, event=None):
        selected = self.table.get_selected()
        # self.kano_button.set_sensitive(selected is not None)
        self.left_button.set_sensitive(selected is not None)
        self.right_button.set_sensitive(selected is not None)


class WallpaperTable(ImageTable):

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

        # Data structure of the wallpapers
        # self.wallpapers = {
        #   image_name: {
        #       'path': path_to_image,
        #       'selected': False,
        #       'unlocked': True,
        #       'button': GtkButton
        #   }
        # }

        # We also have a button_list to determine the order of the buttons
        self.button_list = []
        self.create_wallpaper_dict()

        # Add the buttons to self.button_list
        self.order_packing_of_wallpapers()
        self.attach_buttons_to_table(self.button_list)

    def create_wallpaper_dict(self):
        '''Get the wallpapers from the profile, the Kano Draw pictures
        and find which ones are unlocked
        '''

        self.images = {}

        self.get_wallpapers(wallpaper_path)
        self.get_wallpapers(kano_draw_path)

        cm = ContentManager.from_local()
        for co in cm.list_local_objects(spec='wallpapers'):
            wallpaper_dir = co.get_data('wallpapers').get_dir()
            self.get_wallpapers(wallpaper_dir)

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
        '''Find the list of wallpaper files.
        Go through the paths of the wallpapers and stuff them in the
        dictionary.
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
        '''Fix the order of the packing of the wallpapers by adding
        them in order to a list.
        '''

        # In turn, add the default, unlocked, and finally locked wallpapers
        # using a separate list to account for ordering
        for name, attributes in self.images.iteritems():
            if 'kanux-background' in name:
                self.add_to_button_list(name, True)

        for name, attributes in self.images.iteritems():
            if attributes['unlocked'] and 'kanux-background' not in name:
                self.add_to_button_list(name, True)

        for name, attributes in self.images.iteritems():
            if not attributes['unlocked']:
                self.add_to_button_list(name, False)

    def add_to_button_list(self, name, unlocked=True):
        '''Creates a button from the image and adds to the
        button_list so we can keep track of the order
        '''

        image = self.format_image(name)
        button = self.create_button(name, image, unlocked)
        self.images[name]['button'] = button

        # so we keep the order of the buttons
        self.button_list.append(button)

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
            wallpaper_name = name + name_pattern
            wallpaper_path = os.path.join(self.get_path(name), wallpaper_name)
            wallpaper_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                wallpaper_path, 120, 90
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


class FirstBootSetWallpaper(SetWallpaper):
    def __init__(self, win):
        SetWallpaper.__init__(self, win,
                              header=_("Pick your background"),
                              subheader=_("New wallpapers unlocked! Level up to get more."),
                              buttons_shown=2)
        self.win.set_main_widget(self)

        self.sw.set_margin_bottom(20)
        self.sw.set_margin_top(25)
        self.sw.set_margin_left(25)
        self.sw.set_margin_right(25)
        self.win.set_size_request(680, 600)

        self.win.show_all()

    def apply_changes(self, button, event):
        SetWallpaper.apply_changes(self, button, event)
        Gtk.main_quit()


if __name__ == "__main__":
    from kano.gtk3.application_window import ApplicationWindow

    win = ApplicationWindow("blah", 10, 10)
    wallpaper = FirstBootSetWallpaper(win)

    win.connect('delete-event', Gtk.main_quit)
    win.show_all()

    Gtk.main()
