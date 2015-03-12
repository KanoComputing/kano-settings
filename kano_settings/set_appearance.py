#!/usr/bin/env python

# set_appearence.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functionality for the wallpapers and the screensavers

from gi.repository import Gtk
from kano_settings.set_wallpaper import SetWallpaper
from kano_settings.set_screensaver import SetScreensaver


class SetAppearance(Gtk.Notebook):

    def __init__(self, win):

        Gtk.Notebook.__init__(self)

        background = Gtk.EventBox()
        background.get_style_context().add_class('set_appearance_window')
        background.add(self)

        self.win = win
        self.win.set_main_widget(background)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        # Modify set_wallpaper so it doesn't add itself to the window
        wallpaper_widget = SetWallpaper(self.win)
        screensaver_widget = SetScreensaver(self.win)

        wallpaper_label = Gtk.Label('WALLPAPER')
        screensaver_label = Gtk.Label('SCREENSAVER')

        # Add the screensaver and wallpaper tabs
        self.append_page(wallpaper_widget, wallpaper_label)
        self.append_page(screensaver_widget, screensaver_label)

        self.win.show_all()
