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


def activate(_win, box, apply_changes_button):
    global internet

    title = Gtk.Label("TITLE")
    title.modify_font(Pango.FontDescription("Bariol 16"))
    description = Gtk.Label("Description of project")
    description.modify_font(Pango.FontDescription("Bariol 14"))

    title_style = title.get_style_context()
    title_style.add_class('title')

    description_style = description.get_style_context()
    description_style.add_class('description')

    # Table
    settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    settings_box.set_size_request(300, 250)
    box.add(settings_box)
    settings_box.pack_start(title, False, False, 0)
    settings_box.pack_start(description, False, False, 10)

    # TODO: this should be done when starting the tool and only once
    # Check for internet
    internet = is_internet()

    internet_img = Gtk.Image()

     # Apply button
    event_box = Gtk.EventBox()
    #event_box.set_size_request(200, 200)
    status_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 0)
    event_box.add(status_box)
    event_box_style = event_box.get_style_context()

    internet_status = Gtk.Label()
    internet_status.modify_font(Pango.FontDescription("Bariol bold 12"))
    internet_status_style = internet_status.get_style_context()
    
    internet_action = Gtk.Label()
    internet_action.modify_font(Pango.FontDescription("Bariol bold 11"))
    internet_action_style = internet_action.get_style_context()
    internet_action_style.add_class("white")
    internet_status_style.add_class("internet_status_top")
    internet_action_style.add_class("internet_status_bottom")
    status_box.set_valign(Gtk.Align.CENTER)

    status_box.pack_start(internet_status, False, False, 2)
    status_box.pack_start(internet_action, False, False, 2)
    status_box_style = status_box.get_style_context()


    container = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 0)
    container.pack_start(event_box, False, False, 0)
    container.pack_start(internet_img, False, False, 0)

    settings_box.pack_start(container, False, False, 0)

    #event_box.set_events("button-press-event", self.on_button_press_event)
    event_box.connect("button-press-event", apply_changes)
    
    if internet is False:
        internet_img.set_from_file("media/Graphics/Internet-connection.png")
        title.set_text("Weee you have internet")
        description.set_text("Great!")
        internet_status.set_text("Weee you have internet")
        internet_status_style.remove_class("dark_red")
        internet_status_style.add_class("dark_green")
        internet_action.set_text("Configure")
        event_box_style.add_class("connected")
    else:
        internet_img.set_from_file("media/Graphics/Internet-noConnection.png")
        title.set_text("No network found")
        description.set_text("Shit man")
        internet_status.set_text("No network found")
        internet_status_style.remove_class("dark_green")
        internet_status_style.add_class("dark_red")
        internet_action.set_text("+ Click to add")
        event_box_style.add_class("not_connected")    

    box.pack_start(apply_changes_button, False, False, 0)


def apply_changes(button):
    # Call WiFi config

    os.system('rxvt -title \'WiFi\' -e sudo /usr/bin/kano-wifi')
