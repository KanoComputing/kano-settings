#
# image_table.py
#
# Copyright (C) 2015 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#

import os

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf, GObject
from kano_settings.config_file import username

wallpaper_path = "/usr/share/kano-desktop/wallpapers/"
kano_draw_path = os.path.join('/home', username, 'Draw-content/wallpapers/')
padlock_path = "/usr/share/kano-settings/media/Icons/padlock.png"  # needs to be 95x95
name_pattern = "-4-3.png"


# This is the grid of the images which can be selected
class ImageTable(Gtk.Table):

    # Define a "image_selected" signal which is emitted when an image is
    # selected
    # This is useful to unlock the button in this class's parent window.
    __gsignals__ = {
        'image_selected': (GObject.SIGNAL_RUN_FIRST, None, (bool,))
    }

    def __init__(self, rows, columns, row_padding,
                 column_padding, icon_width, icon_height):

        self.icon_width = icon_width
        self.icon_height = icon_height
        self.row_padding = row_padding
        self.column_padding = column_padding
        self.number_of_rows = rows
        self.number_of_columns = columns

        Gtk.Table.__init__(
            self, self.number_of_rows, self.number_of_columns, True
        )

        self.set_row_spacings(self.row_padding)
        self.set_col_spacings(self.column_padding)

        # The list of items of the form
        # Data structure of the wallpapers
        # self.images = {
        #   image_name: {
        #       'path': path_to_image,
        #       'selected': False,
        #       'unlocked': True,
        #       'button': GtkButton
        #   }
        # }
        self.images = {}

        # To specify the order of packing, we also have a
        # self.button_list
        # This is just to specify the order the buttons should be packed
        self.button_list = []

    def attach_buttons_to_table(self, button_list):
        '''Pack all the buttons in the table
        '''

        # Attach to table
        row = 0
        j = 0

        for button in button_list:
            self.attach(button, j, j + 1, row, row + 1,
                        Gtk.AttachOptions.EXPAND,
                        Gtk.AttachOptions.EXPAND, 0, 0)

            j = (j + 1) % self.number_of_columns
            if j == 0:
                row += 1

    def add_selected_css_class(self, image_name):
        '''Adds the CSS class that shows the image that has been selected,
        even when the mouse is moved away.
        '''

        for name, img_dict in self.images.iteritems():
            button = img_dict['button']
            style = button.get_style_context()
            style.remove_class('wallpaper_box_active')
            style.add_class('wallpaper_box')

        if image_name in self.images:
            button = self.images[image_name]['button']
            style = button.get_style_context()
            style.remove_class('wallpaper_box')
            style.add_class('wallpaper_box_active')

    def select_image_cb(self, widget, event, image_name):
        '''This is connected to the button-release-event when you click on a
        button in the table.
        If the image is unlocked, add the css selected class, select the image
        and emit a signal that the parent window can use
        '''

        if self.images[image_name]['unlocked']:
            self.add_selected_css_class(image_name)
            self.set_selected(image_name)

            # When an image is selected, emit a signal
            self.emit('image_selected', self.images[image_name]['unlocked'])

    def create_button(self, name, image, unlocked=True):
        '''This places the image onto a Gtk.Fixed so we can overlay a padlock
        on top (if the item is locked)
        This is then put onto a Gtk.Button with the appropriate CSS class.
        Returns the button.
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
        button.connect('button-release-event', self.select_image_cb, name)
        return button

    def set_selected(self, image_name):
        '''Sets the selected element in the dictionary to True,
        and sets all the others to False
        '''

        # Unselect current one
        selected = self.get_selected()
        if selected:
            self.images[selected]['selected'] = False

        self.images[image_name]['selected'] = True

    def get_selected(self):
        '''Gets the name of the current selected image
        '''
        for x in self.images:
            if self.images[x]['selected']:
                return x

    def unselect_all(self):
        '''Remove all styling on all images, and sets the 'selected'
        field to False
        '''

        for x in self.images:
            self.images[x]['selected'] = False
        self.add_selected_css_class(None)
