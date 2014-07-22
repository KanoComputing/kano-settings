#!/usr/bin/env python

# set_overscan
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for share screen

import os
from gi.repository import Gtk
from kano.gtk3.heading import Heading
import kano_settings.constants as constants
from kano.utils import run_cmd
from .functions import get_overscan_status, write_overscan_values, set_overscan_status

overscan_pipe = "/var/tmp/overscan"
overscan_values = None
button = None


def activate(_win, box, _button):
    global overscan_values

    button = _button

    # Launch pipeline
    if not os.path.exists(overscan_pipe):
        run_cmd('mknod {} c 100 0'.format(overscan_pipe))
    overscan_values = get_overscan_status()

    # Header
    title = Heading("Overscan", "")
    box.pack_start(title.container, False, False, 0)

    # Add sliders
    grid = Gtk.Grid()
    grid.set_row_spacing(0)
    ## Top slider
    t_scale = Gtk.HScale.new_with_range(0, 100, 1)
    t_scale.set_value(overscan_values['top'])
    t_scale.set_size_request(400, 30)
    t_scale.connect('value_changed', adjust, 'top')
    grid.attach(t_scale, 0, 0, 1, 1)
    ## Bottom slider
    b_scale = Gtk.HScale.new_with_range(0, 100, 1)
    b_scale.set_value(overscan_values['bottom'])
    b_scale.set_size_request(400, 30)
    b_scale.connect('value_changed', adjust, 'bottom')
    grid.attach(b_scale, 0, 1, 1, 1)
    ## Left slider
    l_scale = Gtk.HScale.new_with_range(0, 100, 1)
    l_scale.set_value(overscan_values['left'])
    l_scale.set_size_request(400, 30)
    l_scale.connect('value_changed', adjust, 'left')
    grid.attach(l_scale, 0, 2, 1, 1)
    ## Right slider
    r_scale = Gtk.HScale.new_with_range(0, 100, 1)
    r_scale.set_value(overscan_values['right'])
    r_scale.set_size_request(400, 30)
    r_scale.connect('value_changed', adjust, 'right')
    grid.attach(r_scale, 0, 3, 1, 1)

    align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    padding = 5
    align.set_padding(padding, padding, padding, padding)
    align.add(grid)
    box.pack_start(align, False, False, 0)

    # Add Changes button
    box.pack_start(button.align, False, False, 0)
    _win.show_all()


def apply_changes(button):
    # Apply changes
    write_overscan_values(overscan_values)

    # Tell user to reboot to see changes
    constants.need_reboot = True


def adjust(adj, varname):
    global overscan_values

    overscan_values[varname] = int(adj.get_value())
    set_overscan_status(overscan_values)


