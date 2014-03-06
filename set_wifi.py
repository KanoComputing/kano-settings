#!/usr/bin/env python3

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
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


def activate(_win, table, box, title, description):
    global internet

    # Title
    title.set_text("Wifi")
    # Description
    description.set_text("Let me talk to the world")
    # Table
    table = Gtk.Table(4, 1, True)
    box.add(table)

    # TODO: this should be done when starting the tool and only once
    # Check for internet
    internet = is_internet()

    if internet is False:
        label = Gtk.Label()
        label.set_text("Weee you have internet")
        label.set_justify(Gtk.Justification.LEFT)
        table.attach(label, 0, 1, 1, 2)
    else:
        # Apply button
        button = Gtk.Button("Set WiFi")
        button.connect("clicked", apply_changes)
        table.attach(button, 0, 1, 3, 4)


def apply_changes(button):
    # Call WiFi config

    os.system('rxvt -title \'WiFi\' -e sudo /usr/bin/kano-wifi')
