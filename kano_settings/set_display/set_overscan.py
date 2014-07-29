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
from kano.gtk3.buttons import OrangeButton
import kano_settings.constants as constants
from kano.utils import run_cmd
from .functions import get_overscan_status, write_overscan_values, set_overscan_status, \
    get_model
from ..boot_config import set_config_comment

overscan_pipe = "/var/tmp/overscan"
overscan_values = None
original_overscan = None
win = None
box = None
button = None
# sliders
t_scale = None
b_scale = None
l_scale = None
r_scale = None


def activate(_win, _box, _button):
    global overscan_values, original_overscan, win, box, button

    win = _win
    box = _box
    button = _button

    # Launch pipe
    if not os.path.exists(overscan_pipe):
        run_cmd('mknod {} c 100 0'.format(overscan_pipe))

    overscan_values = get_overscan_status()
    original_overscan = get_overscan_status()

    # Display first simple overscan
    simple_overscan()


def simple_overscan():
    global win, box, button, t_scale

    # Listen for key events
    win.connect("key-press-event", on_key_press)
    # Header
    title = Heading("Overscan", "")
    box.pack_start(title.container, False, False, 0)

    # Add sliders
    grid = Gtk.Grid()
    grid.set_row_spacing(0)
    ## slider
    t_scale = Gtk.HScale.new_with_range(0, 100, 1)
    t_scale.set_value(overscan_values['top'])
    t_scale.set_size_request(400, 30)
    t_scale.connect('value_changed', adjust_all)
    grid.attach(t_scale, 0, 0, 1, 1)

    # Advance button
    advance_button = OrangeButton()
    advance_button.connect("button_press_event", go_to_advance)
    advance_button.set_label("Advance")
    grid.attach(advance_button, 0, 2, 1, 1)

    # Reset button
    reset_button = OrangeButton()
    reset_button.connect("button_press_event", reset_simple)
    reset_button.set_label("Reset")
    grid.attach(reset_button, 0, 3, 1, 1)

    align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    padding = 5
    align.set_padding(padding, padding, padding, padding)
    align.add(grid)
    box.pack_start(align, False, False, 0)

    # Add Changes button
    box.pack_start(button.align, False, False, 0)

    win.show_all()


def advance_overscan():
    global box, button, t_scale, b_scale, l_scale, r_scale

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
    top_label = Gtk.Label()
    top_label.set_alignment(xalign=1, yalign=0.5)
    top_label.set_text('Top')
    grid.attach(top_label, 1, 0, 1, 1)
    ## Bottom slider
    b_scale = Gtk.HScale.new_with_range(0, 100, 1)
    b_scale.set_value(overscan_values['bottom'])
    b_scale.set_size_request(400, 30)
    b_scale.connect('value_changed', adjust, 'bottom')
    grid.attach(b_scale, 0, 1, 1, 1)
    bottom_label = Gtk.Label()
    bottom_label.set_alignment(xalign=1, yalign=0.5)
    bottom_label.set_text('Bottom')
    grid.attach(bottom_label, 1, 1, 1, 1)
    ## Left slider
    l_scale = Gtk.HScale.new_with_range(0, 100, 1)
    l_scale.set_value(overscan_values['left'])
    l_scale.set_size_request(400, 30)
    l_scale.connect('value_changed', adjust, 'left')
    grid.attach(l_scale, 0, 2, 1, 1)
    left_label = Gtk.Label()
    left_label.set_alignment(xalign=1, yalign=0.5)
    left_label.set_text('Left')
    grid.attach(left_label, 1, 2, 1, 1)
    ## Right slider
    r_scale = Gtk.HScale.new_with_range(0, 100, 1)
    r_scale.set_value(overscan_values['right'])
    r_scale.set_size_request(400, 30)
    r_scale.connect('value_changed', adjust, 'right')
    grid.attach(r_scale, 0, 3, 1, 1)
    right_label = Gtk.Label()
    right_label.set_alignment(xalign=1, yalign=0.5)
    right_label.set_text('Right')
    grid.attach(right_label, 1, 3, 1, 1)

    # Reset button
    reset_button = OrangeButton()
    reset_button.connect("button_press_event", reset_advance)
    reset_button.set_label("Reset")
    grid.attach(reset_button, 0, 4, 1, 1)

    align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    padding = 5
    align.set_padding(padding, padding, padding, padding)
    align.add(grid)
    box.pack_start(align, False, False, 0)

    # Add Changes button
    box.pack_start(button.align, False, False, 0)

    win.show_all()


def on_key_press(widget, event):
    global overscan_values, t_scale
    # Right arrow (65363)
    if not hasattr(event, 'keyval') or event.keyval == 65363:
        overscan_values['top'] += 1
        overscan_values['bottom'] += 1
        overscan_values['left'] += 1
        overscan_values['right'] += 1
        set_overscan_status(overscan_values)
        t_scale.set_value(overscan_values['top'])
        return
    # Left arrow (65361)
    if not hasattr(event, 'keyval') or event.keyval == 65361:
        overscan_values['top'] -= 1
        overscan_values['bottom'] -= 1
        overscan_values['left'] -= 1
        overscan_values['right'] -= 1
        set_overscan_status(overscan_values)
        t_scale.set_value(overscan_values['top'])
        return


def go_to_advance(event=None, arg=None):
    global box
    # Remove children
    for i in box.get_children():
        box.remove(i)
    advance_overscan()


def reset_simple(event=None, arg=None):
    global t_scale
    # Restore overscan if any
    if original_overscan != overscan_values:
        set_overscan_status(original_overscan)
        t_scale.set_value(original_overscan['top'])


def reset_advance(event=None, arg=None):
    global t_scale, b_scale, l_scale, r_scale
    # Restore overscan if any
    if original_overscan != overscan_values:
        set_overscan_status(original_overscan)
        t_scale.set_value(original_overscan['top'])
        b_scale.set_value(original_overscan['bottom'])
        l_scale.set_value(original_overscan['left'])
        r_scale.set_value(original_overscan['right'])


def apply_changes(button):
    # Apply changes
    write_overscan_values(overscan_values)
    set_config_comment('kano_screen_used', get_model())

    # Tell user to reboot to see changes
    constants.need_reboot = True


def adjust(adj, varname):
    global overscan_values

    overscan_values[varname] = int(adj.get_value())
    set_overscan_status(overscan_values)


def adjust_all(adj):
    global overscan_values

    overscan_values['top'] = int(adj.get_value())
    overscan_values['bottom'] = int(adj.get_value())
    overscan_values['left'] = int(adj.get_value())
    overscan_values['right'] = int(adj.get_value())
    set_overscan_status(overscan_values)
