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
from ..config_file import file_replace

boot_config_file = "/boot/config.txt"
overscan_pipe = "/var/tmp/overscan"
overscan_values = {
    'top': 0,
    'bottom': 0,
    'left': 0,
    'right': 0,
}
button = None


def activate(_win, box, _button):

    button = _button

    # Launch pipeline
    if not os.path.exists(overscan_pipe):
        run_cmd('mknod {} c 100 0'.format(overscan_pipe))
    get_overscan_status()

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

    top_pattern = "overscan_top=[0-9]*[0-9]*[0-9]"
    bottom_pattern = "overscan_bottom=[0-9]*[0-9]*[0-9]"
    left_pattern = "overscan_left=[0-9]*[0-9]*[0-9]"
    right_pattern = "overscan_right=[0-9]*[0-9]*[0-9]"
    top = "overscan_top=" + str(overscan_values['top'])
    bottom = "overscan_bottom=" + str(overscan_values['bottom'])
    left = "overscan_left=" + str(overscan_values['left'])
    right = "overscan_right=" + str(overscan_values['right'])

    # Apply changes
    file_replace(boot_config_file, top_pattern, top)
    file_replace(boot_config_file, bottom_pattern, bottom)
    file_replace(boot_config_file, left_pattern, left)
    file_replace(boot_config_file, right_pattern, right)

    # Tell user to reboot to see changes
    constants.need_reboot = True


def adjust(adj, varname):
    global overscan_values

    overscan_values[varname] = int(adj.get_value())
    set_overscan_status()


def set_overscan_status():
    #print overscan_values

    top = overscan_values['top']
    bottom = overscan_values['bottom']
    left = overscan_values['left']
    right = overscan_values['right']

    cmd = 'overscan {} {} {} {}'.format(top, bottom, left, right)
    run_cmd(cmd)


def get_overscan_status():
    global overscan_values

    out, _, _ = run_cmd('overscan')
    try:
        top, bottom, left, right = out.strip().split()
    except Exception:
        top = left = right = bottom = 0

    top = int(top)
    bottom = int(bottom)
    left = int(left)
    right = int(right)

    overscan_values = {
        'top': top,
        'bottom': bottom,
        'left': left,
        'right': right,
    }
