#!/usr/bin/env python

# set_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.components.heading as heading
import kano_settings.constants as constants


def activate(win, box, apply_changes):
    title = heading.Heading("You just made a computer", "Now I just need to ask a few questions, so I'll work out the way")

    image = Gtk.Image()
    image.set_from_file(constants.media + "/Graphics/Intro-illustration.png")

    image_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    image_box.pack_start(image, False, False, 0)
    image_box.pack_start(title.container, False, False, 0)
    image_box.set_size_request(450, 250)

    box.pack_start(image_box, False, False, 0)
    box.pack_start(apply_changes.button, False, False, 0)

    apply_changes.text.set_text("Get started")

    # button needs to have label - get started >


def apply_changes(button):
    return
