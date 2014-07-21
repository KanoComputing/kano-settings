#!/usr/bin/env python

# set_advance.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.heading import Heading
from kano.gtk3 import kano_dialog
from kano import logging

from kano_settings.components import fixed_size_box

win = None
button = None
box = None

debug_mode = None
CONTAINER_HEIGHT = 70


def activate(_win, _box, _button, parental_button):
    global button, box, win

    win = _win
    box = _box
    button = _button
    button.set_sensitive(False)

    # read debug mode
    debug_mode = get_stored_debug_mode()

    title = Heading("Advanced options", "Toggle parental lock and debug mode")
    box.pack_start(title.container, False, False, 0)

    # Contains main buttons
    settings = fixed_size_box.Fixed()

    box.pack_start(settings.box, False, False, 0)

    vertical_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=40)
    vertical_container.set_valign(Gtk.Align.CENTER)

    # Parental lock check button
    parental_button.set_can_focus(False)
    parental_button.props.valign = Gtk.Align.CENTER
    parental_button.get_style_context().add_class("bold_toggle")
    parental_info = Gtk.Label("Restrict online content")
    parental_info.get_style_context().add_class("normal_label")

    parental_box = Gtk.Box()
    parental_box.pack_start(parental_button, False, False, 0)
    parental_box.pack_start(parental_info, False, False, 0)

    vertical_container.pack_start(parental_box, False, False, 0)

    # Debug mode check button
    debug_button = Gtk.CheckButton("Debug mode")
    debug_button.set_can_focus(False)
    debug_button.props.valign = Gtk.Align.CENTER
    debug_button.set_active(debug_mode)
    debug_button.connect("clicked", on_debug_toggled)
    debug_button.get_style_context().add_class("bold_toggle")
    debug_info = Gtk.Label("Having problems? Enable this mode and report a bug")
    debug_info.get_style_context().add_class("normal_label")

    debug_box = Gtk.Box()
    debug_box.pack_start(debug_button, False, False, 0)
    debug_box.pack_start(debug_info, False, False, 0)

    vertical_container.pack_start(debug_box, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    valign.add(vertical_container)
    valign.set_padding(20, 0, 0, 0)
    settings.box.pack_start(valign, False, False, 0)

    # Add apply changes button under the main settings content
    box.pack_start(button.align, False, False, 0)
    win.show_all()


def apply_changes(button):
    global debug_mode

    old_debug_mode = get_stored_debug_mode()
    if debug_mode == old_debug_mode:
        logging.Logger().debug('skipping debug mode change')
        return

    if debug_mode:
        # set debug on:
        logging.set_system_log_level('debug')
        logging.Logger().info('setting logging to debug')
        msg = "Activated"
    else:
        # set debug off:
        logging.set_system_log_level('error')
        logging.Logger().info('setting logging to error')
        msg = "De-activated"

    kdialog = kano_dialog.KanoDialog("Debug mode", msg, parent_window=win)
    kdialog.run()

    # update new debug mode
    debug_mode = get_stored_debug_mode()

    button.set_sensitive(False)


def on_debug_toggled(checkbutton):
    global debug_mode, button

    debug_mode = checkbutton.get_active()
    button.set_sensitive(True)


def get_stored_debug_mode():
    ll = logging.Logger().get_log_level()
    debug_mode = ll == 'debug'
    logging.Logger().debug('stored debug-mode: {}'.format(debug_mode))
    return ll == 'debug'
