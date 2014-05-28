#!/usr/bin/env python

# set_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.components.heading as heading
import kano_settings.constants as constants
import kano_settings.components.fixed_size_box as fixed_size_box
IMG_HEIGHT = 96


def activate(win, box, update):

    title = heading.Heading("You just made a computer", "Now I just need to ask a few questions, so I'll work out the way")

    settings = fixed_size_box.Fixed()

    image = Gtk.Image()
    image.set_from_file(constants.media + "/Graphics/Intro-illustration.png")

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - IMG_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(image)
    settings.box.pack_start(valign, False, False, 0)

    win.top_bar.prev_button.set_image(win.top_bar.pale_prev_arrow)
    win.top_bar.next_button.set_image(win.top_bar.dark_next_arrow)

    box.pack_start(settings.box, False, False, 0)
    box.pack_start(title.container, False, False, 0)
    box.pack_start(update.align, False, False, 0)

    update.set_sensitive(True)


def apply_changes(button):
    return
