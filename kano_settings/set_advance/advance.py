#!/usr/bin/env python

# set_advance.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano.gtk3.kano_dialog as kano_dialog
import kano_settings.components.fixed_size_box as fixed_size_box
import kano.logging as logging

win = None
button = None
box = None

parental_mode = None
debug_mode = None
CONTAINER_HEIGHT = 70


def activate(_win, _box, _button, parental_button):
    global button, box, win, parental_mode

    win = _win
    box = _box
    button = _button
    button.set_sensitive(False)

    # read debug mode
    debug_mode = get_stored_debug_mode()

    # read parental mode ...
    # parental_mode = get_setting("Parental-lock")

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
    parental_info = Gtk.Label("ENABLE PARENTAL MODE")
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
    debug_info = Gtk.Label("ENABLE DEBUGGING")
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
    old_debug_mode = get_stored_debug_mode()
    if debug_mode == old_debug_mode:
        logging.logger.debug('skipping debug mode change')
        return

    if debug_mode:
        # set debug on:
        logging.set_system_log_level('debug')
        logging.logger.info('setting logging to debug')
        msg = "Activated"
    else:
        # set debug off:
        logging.set_system_log_level('error')
        logging.logger.info('setting logging to error')
        msg = "De-activated"

    kdialog = kano_dialog.KanoDialog("Debug mode", msg)
    kdialog.run()

    button.set_sensitive(False)


def on_debug_toggled(checkbutton):
    global debug_mode, button

    debug_mode = checkbutton.get_active()
    button.set_sensitive(True)


def get_stored_debug_mode():
    ll = logging.logger.get_log_level()
    debug_mode = ll == 'debug'
    logging.logger.debug('stored debug-mode: {}'.format(debug_mode))
    return ll == 'debug'
