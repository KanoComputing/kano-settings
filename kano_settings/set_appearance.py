#!/usr/bin/env python

# set_appearence.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Functionality for the wallpapers and the screensavers

from gi.repository import Gtk
from kano_settings.set_wallpaper import SetWallpaper
from kano_settings.set_screensaver import SetScreensaver


class SetAppearance(Gtk.Notebook):
    # get labels here

    def __init__(self, win):

        Gtk.Notebook.__init__(self)
        self.win = win
        self.win.set_main_widget(self)

        self.connect("switch-page", self._switch_page)

        # Modify set_wallpaper so it doesn't add itself to the window
        wallpaper_widget = SetWallpaper(self.win)
        screensaver_widget = SetScreensaver(self.win)

        # add the screensaver and wallpaper tabs
        # self.append_page(screensaver_widget, 'Screensaver')
        self.append_page(wallpaper_widget, 'Wallpaper')
        self.append_page(screensaver_widget, 'Screensaver')

    def _switch_page(self, notebook, page, page_num, data=None):
        self._window.set_last_page(page_num)
