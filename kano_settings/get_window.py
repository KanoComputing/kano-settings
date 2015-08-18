#!/usr/bin/env python

# Custom window base class
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# You can use this as a base for you application's window in case
# you'd like to blur it.
# Has option to also base this on a Gtk.Plug


from gi.repository import Gtk, Gdk
from kano.gtk3.apply_styles import apply_common_to_screen, apply_styling_to_screen
from kano.logging import logger


def get_window_class(plug=False):
    if plug:
        logger.debug("Launching as a Gtk.Plug")
        return application_window_wrapper(Gtk.Plug)
    else:
        logger.debug("Launching as a Gtk.Window")
        return application_window_wrapper(Gtk.Window)


def application_window_wrapper(base_class):

    class ApplicationWindow(base_class):

        def __init__(self, title="Application", width=None, height=None,
                     socket_id=0):

            base_class.__init__(self, title=title)
            self._base_name = base_class.__name__

            if self._base_name == "Plug":
                self.construct(int(socket_id))
                self.get_style_context().add_class("plug")
            else:
                self.set_position(Gtk.WindowPosition.CENTER)

            self.set_decorated(False)
            self.set_resizable(False)

            screen = Gdk.Screen.get_default()
            self._win_width = width
            if width <= 1:
                self._win_width = int(screen.get_width() * width)

            self._win_height = height
            if height <= 1:
                self._win_height = int(screen.get_height() * height)
            self.set_size_request(self._win_width, self._win_height)

            self.connect('delete-event', Gtk.main_quit)

            self._overlay = Gtk.Overlay()
            self.add(self._overlay)

            self._blur = Gtk.EventBox()
            self._blur.get_style_context().add_class('blur')

            self._blurred = False

        def add_plug_class(self, widget):
            if self._base_name == "Plug":
                widget.get_style_context().add_class("plug")

        def blur(self):
            if not self._blurred:
                self._overlay.add_overlay(self._blur)
                self._blur.show()
                self._blurred = True

        def unblur(self):
            if self._blurred:
                self._overlay.remove(self._blur)
                self._blurred = False

        def set_main_widget(self, widget):
            self._overlay.add(widget)

        def remove_main_widget(self):
            for w in self._overlay.get_children():
                self._overlay.remove(w)

    # Don't initialise the class
    return ApplicationWindow
