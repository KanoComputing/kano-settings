#!/usr/bin/env python3

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import os

internet = False


# TODO: Use the function in kanowifilib.py
def is_internet():
    '''
    Ping Google DNS servers avoiding name resolution delays for faster response time
    '''
    try:
        rc = os.system('ping -c 1 8.8.8.8 > /dev/null 2>&1')
        return rc == 0
    except:
        return False


def activate(_win, box, title_container, apply_changes):
    global internet

    title = Gtk.Label("TITLE")
    title.modify_font(Pango.FontDescription("Bariol 16"))
    description = Gtk.Label("Description of project")
    description.modify_font(Pango.FontDescription("Bariol 14"))

    title_style = title.get_style_context()
    title_style.add_class('title')

    description_style = description.get_style_context()
    description_style.add_class('description')

    # Title
    title.set_text("Wifi")
    # Description
    description.set_text("Let me talk to the world")
    # Table
    settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    settings_box.set_size_request(450, 250)
    box.add(settings_box)

    # TODO: this should be done when starting the tool and only once
    # Check for internet
    internet = is_internet()

    if internet is False:
        label = Gtk.Label()
        label.set_text("Weee you have internet")
        label.set_justify(Gtk.Justification.LEFT)
        settings_box.pack_start(label, False, False, 0)
    else:
        # Apply button
        button = Gtk.Button("Set WiFi")
        button.connect("clicked", apply_changes)
        settings_box.pack_start(button, False, False, 0)

    box.pack_start(apply_changes, False, False, 0)


def apply_changes(button):
    # Call WiFi config

    os.system('rxvt -title \'WiFi\' -e sudo /usr/bin/kano-wifi')
