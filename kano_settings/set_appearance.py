#!/usr/bin/env python

# set_appearence.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functionality for the wallpapers and the screensavers

from gi.repository import Gtk
# from kano_settings.set_wallpaper import SetWallpaper
# from kano_settings.set_screensaver import SetScreensaver
from kano_settings.set_image import SetWallpaper, SetScreensaver


class SetAppearance(Gtk.Notebook):
    # get labels here

    def __init__(self, win):

        Gtk.Notebook.__init__(self)

        self.win = win
        background = Gtk.EventBox()
        background.get_style_context().add_class('set_appearance_window')
        background.add(self)

        self.win.set_main_widget(background)

        # self.connect("switch-page", self._switch_page)

        # Modify set_wallpaper so it doesn't add itself to the window
        wallpaper_widget = SetWallpaper(self.win)
        screensaver_widget = SetScreensaver(self.win)

        wallpaper_label = Gtk.Label('WALLPAPER')
        screensaver_label = Gtk.Label('SCREENSAVER')

        # Add the screensaver and wallpaper tabs
        self.append_page(wallpaper_widget, wallpaper_label)
        self.append_page(screensaver_widget, screensaver_label)

        self.win.show_all()
