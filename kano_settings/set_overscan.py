#!/usr/bin/env python

# set_overscan
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for share screen

import os
from gi.repository import Gtk
from kano_settings.templates import Template
import kano_settings.constants as constants
from kano.utils import run_cmd
from .functions import get_overscan_status, write_overscan_values, set_overscan_status, \
    get_model
from ..boot_config import set_config_comment


class SetOverscan(Template):

    def __init__(self):
        Template.__init__(self, "Overscan", "", "APPLY CHANGES")
        self.kano_button.connect("button-press-release", self.apply_changes)

        self.win.add(self)

        # Launch pipeline
        if not os.path.exists(self.overscan_pipe):
            run_cmd('mknod {} c 100 0'.format(self.overscan_pipe))

        self.overscan_values = get_overscan_status()

        # Add sliders
        grid = Gtk.Grid()
        grid.set_row_spacing(0)
        ## Top slider
        t_scale = Gtk.HScale.new_with_range(0, 100, 1)
        t_scale.set_value(self.overscan_values['top'])
        t_scale.set_size_request(400, 30)
        t_scale.connect('value_changed', self.adjust, 'top')
        grid.attach(t_scale, 0, 0, 1, 1)
        ## Bottom slider
        b_scale = Gtk.HScale.new_with_range(0, 100, 1)
        b_scale.set_value(self.overscan_values['bottom'])
        b_scale.set_size_request(400, 30)
        b_scale.connect('value_changed', self.adjust, 'bottom')
        grid.attach(b_scale, 0, 1, 1, 1)
        ## Left slider
        l_scale = Gtk.HScale.new_with_range(0, 100, 1)
        l_scale.set_value(self.overscan_values['left'])
        l_scale.set_size_request(400, 30)
        l_scale.connect('value_changed', self.adjust, 'left')
        grid.attach(l_scale, 0, 2, 1, 1)
        ## Right slider
        r_scale = Gtk.HScale.new_with_range(0, 100, 1)
        r_scale.set_value(self.overscan_values['right'])
        r_scale.set_size_request(400, 30)
        r_scale.connect('value_changed', self.adjust, 'right')
        grid.attach(r_scale, 0, 3, 1, 1)

        self.box.pack_start(grid, False, False, 0)

        self.win.show_all()

    def apply_changes(self, button, event):
        # Apply changes
        write_overscan_values(self.overscan_values)
        set_config_comment('kano_screen_used', get_model())

        # Tell user to reboot to see changes
        constants.need_reboot = True

    def adjust(self, adj, varname):
        self.overscan_values[varname] = int(adj.get_value())
        set_overscan_status(self.overscan_values)


