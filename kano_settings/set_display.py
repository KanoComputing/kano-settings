#!/usr/bin/env python

# set_display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano_settings.templates import Template
from kano.gtk3.buttons import OrangeButton
import kano_settings.constants as constants
from kano_settings.boot_config import set_config_comment
from kano.utils import run_cmd
from kano_settings.display.functions import get_model, list_supported_modes, set_hdmi_mode, read_hdmi_mode, \
    find_matching_mode, get_overscan_status, write_overscan_values, set_overscan_status


class SetDisplay(Template):

    def __init__(self, win):

         # Get display name
        self.model = get_model()

        Template.__init__(self, "Display", self.model, "APPLY CHANGES")

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.win.go_to_home)

        self.kano_button.set_sensitive(False)
        self.kano_button.connect("button-release-event", self.apply_changes)

        horizontal_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
        horizontal_container.set_valign(Gtk.Align.CENTER)

        # HDMI mode combo box
        self.mode_combo = Gtk.ComboBoxText.new()
        self.mode_combo.connect("changed", self.on_mode_changed)

        # Fill list of modes
        modes = list_supported_modes()
        self.mode_combo.append_text("auto")
        if modes:
            for v in modes:
                self.mode_combo.append_text(v)

        horizontal_container.pack_start(self.mode_combo, False, False, 0)
        self.mode_combo.props.valign = Gtk.Align.CENTER

        # Select the current setting in the dropdown list
        saved_group, saved_mode = read_hdmi_mode()
        active_item = find_matching_mode(modes, saved_group, saved_mode)
        self.mode_combo.set_active(active_item)

        # Overscan button
        overscan_button = OrangeButton("Overscan")
        horizontal_container.pack_end(overscan_button, False, False, 0)
        overscan_button.connect("button-release-event", self.go_to_overscan)

        self.box.pack_start(horizontal_container, False, False, 0)

        # Add apply changes button under the main settings content
        self.win.show_all()

    def apply_changes(self, button, event):
        # Set HDMI mode
        # Get mode:group string
        # Of the form "auto" or "cea:1" or "dmt:1" etc.
        parse_mode = self.mode.split(" ")[0]

        self.set_hdmi_mode_from_str(parse_mode)

        constants.need_reboot = True

    def on_mode_changed(self, combo):

        #  Get the selected mode
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            self.model = combo.get_model()
            self.mode = self.model[tree_iter][0]

        self.mode_index = combo.get_active()

        self.kano_button.set_sensitive(True)

    def set_hdmi_mode_from_str(self, mode):
        if mode == "auto":
            set_hdmi_mode()
            set_config_comment('kano_screen_used', 'xxx')
            return

        group, number = mode.split(":")
        set_hdmi_mode(group, number)
        set_config_comment('kano_screen_used', self.model)

    def go_to_overscan(self, widget, event):
        self.win.clear_win()
        SetOverscan(self.win)


class SetOverscan(Template):
    overscan_pipe = "/var/tmp/overscan"

    def __init__(self, win):
        Template.__init__(self, "Overscan", "", "APPLY CHANGES")
        self.kano_button.connect("button-release-event", self.apply_changes)

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()
        self.top_bar.set_prev_callback(self.go_to_display)

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

    def go_to_display(self, widget, button):
        self.win.clear_win()
        SetDisplay(self.win)

    def apply_changes(self, button, event):
        # Apply changes
        write_overscan_values(self.overscan_values)
        set_config_comment('kano_screen_used', get_model())

        # Tell user to reboot to see changes
        constants.need_reboot = True

    def adjust(self, adj, varname):
        self.overscan_values[varname] = int(adj.get_value())
        set_overscan_status(self.overscan_values)

