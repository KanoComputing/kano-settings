#!/usr/bin/env python3

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import os
import re

HDMI = False


def file_replace(fname, pat, s_after):
    # first, see if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            return  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def activate(_win, table, box):

    

    # Table
    table = Gtk.Table(4, 1, True)
    box.add(table)

    # Label
    label = Gtk.Label()
    label.set_text("Audio")
    label.set_justify(Gtk.Justification.LEFT)
    table.attach(label, 0, 1, 0, 1)

    # Analog radio button
    button1 = Gtk.RadioButton.new_with_label_from_widget(None, "Analog")
    table.attach(button1, 0, 1, 1, 2)
    # HDMI radio button
    button2 = Gtk.RadioButton.new_from_widget(button1)
    button2.set_label("HDMI")
    button2.connect("toggled", on_button_toggled)

    # Show the current setting by electing the appropriate radio button
    current_setting(button1, button2)

    table.attach(button2, 0, 1, 2, 3)

    # Apply button
    button = Gtk.Button("Apply changes")
    button.connect("clicked", apply_changes)
    table.attach(button, 0, 1, 3, 4)


def apply_changes(button):
    global HDMI
    # amixer -c 0 cset numid=3 N
    # 1 analog
    # 2 hdmi

    file_name = "/etc/rc.local"
    pattern = "amixer -c 0 cset numid=3 [0-9]"
    new_line = None
    if HDMI is True:
        new_line = "amixer -c 0 cset numid=3 2"
    else:
        new_line = "amixer -c 0 cset numid=3 1"
    file_replace(file_name, pattern, new_line)


def current_setting(analogue_button, hdmi_button):

    file_name = "/etc/rc.local"
    f = open(file_name, 'r')
    file_string = str(f.read())
    analogue_string = "amixer -c 0 cset numid=3 1"
    hdmi_string = "amixer -c 0 cset numid=3 2"

    if file_string.find(analogue_string) != -1:
        analogue_button.set_active(True)

    elif file_string.find(hdmi_string) != -1:
        hdmi_button.set_active(True)

    # Default, first button is active



def on_button_toggled(button):
    global HDMI

    HDMI = button.get_active()
