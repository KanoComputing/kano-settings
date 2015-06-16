#!/usr/bin/env python

# home_screen.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from gi.repository import Gtk
import math

from kano.gtk3.scrolled_window import ScrolledWindow

from kano_settings.screens import SCREENS



class UnknownScreenError(Exception):
    pass


class HomeScreen(Gtk.Box):
    _DISPLAYED_SCREENS = SCREENS.get_screens_on_home()

    def __init__(self, win, screen_number=None, screen_name=None):
        self.win = win

        # Check if we want to initialise another window first
        if screen_name:
            self.go_to_screen(screen_name)
            return

        if screen_number is not None:
            self.go_to_screen_number(screen_number)
            return

        Gtk.Box.__init__(self)

        self.win.set_main_widget(self)
        self.win.top_bar.disable_prev()
        self.win.remove_prev_callback()

        self.width = 640
        self.height = 304
        self._col_count = 2

        scrolled_window = self._generate_grid()
        self.pack_start(scrolled_window, True, True, 0)

        self.win.show_all()


    def _generate_grid(self):
        row_count = int(math.ceil(
            float(len(self._DISPLAYED_SCREENS)) / self._col_count)
        )

        table = Gtk.Table(row_count, self._col_count, homogeneous=True,
                          hexpand=True, vexpand=True)
        table.props.margin = 0

        for idx, screen in enumerate(self._DISPLAYED_SCREENS):
            row = idx / 2
            col = idx % 2

            screen.create_menu_button(self._change_screen_cb)

            if row % 2:
                style_class = 'appgrid_grey'
            else:
                style_class = 'appgrid_white'

            screen.menu_button.button.get_style_context().add_class(style_class)

            screen.refresh_menu_button()

            table.attach(screen.menu_button.button,
                         col, col + 1, row, row + 1,
                         Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                         Gtk.AttachOptions.FILL, 0, 0)


        scrolled_window = ScrolledWindow(wide_scrollbar=True, vexpand=True,
                                         hexpand=True)
        scrolled_window.get_style_context().add_class("app-grid")
        scrolled_window.add_with_viewport(table)

        return scrolled_window

    def update_intro(self):
        """
        This is to update the introduction text, so that if the settings are
        modified and then we go back to the intro screen, the latest information
        is shown
        """

        for screen in self._DISPLAYED_SCREENS:
            screen.refresh_menu_button()


    def _change_screen_cb(self, screen, screen_name):
        self.go_to_screen(screen_name)


    def go_to_screen(self, screen_name):
        self.win.state = screen_name
        self.win.last_level_visited = screen_name

        self.win.clear_win()

        try:
            screen = SCREENS[screen_name]
        except KeyError:
            msg = "State {} not recognised".format(screen_name)
            raise UnknownScreenError(msg)

        screen.screen_widget(self.win)

    def go_to_screen_number(self, screen_number):
        screen = SCREENS.get_screen_from_number(screen_number)
        screen.screen_widget(self.win)
