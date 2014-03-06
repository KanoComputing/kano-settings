#!/usr/bin/env python3

# set_intro.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk

import set_keyboard
import set_display
import set_audio
import set_wifi
import set_email

def activate(win, grid, box, title, description):

    image = Gtk.Image()
    image.set_from_file("media/Graphics/Intro-illustration.png")
    box.add(image)

    title.set_text("You just made a computer!")
    description.set_text("Now I just need to ask a few questions, so I'll work out the way")

    # button needs to have label - get started >

def apply_changes(button):

    return
