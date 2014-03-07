#!/usr/bin/env python3

# set_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango

import set_keyboard
import set_display
import set_audio
import set_wifi
import set_email

def activate(win, box, apply_changes):

    title = Gtk.Label("TITLE")
    title.modify_font(Pango.FontDescription("Bariol 16"))
    description = Gtk.Label("Description of project")
    description.modify_font(Pango.FontDescription("Bariol 14"))

    title_style = title.get_style_context()
    title_style.add_class('title')

    description_style = description.get_style_context()
    description_style.add_class('description')

    title_container = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=0)
    title_container.add(title)
    title_container.set_size_request(450, 100)
    title_container.pack_start(description, True, True, 10)
    info_style = title_container.get_style_context()
    info_style.add_class('title_container')

    title.set_text("You just made a computer!")
    description.set_text("Now I just need to ask a few questions, so I'll work out the way")

    image = Gtk.Image()
    image.set_from_file("media/Graphics/Intro-illustration.png")

    image_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    image_box.pack_start(image, False, False, 0)
    image_box.pack_start(title_container, False, False, 0)
    image_box.set_size_request(450, 250)

    box.pack_start(image_box, False, False, 0)
    box.pack_end(apply_changes, False, False, 0)

    # button needs to have label - get started >

def apply_changes(button):

    return
