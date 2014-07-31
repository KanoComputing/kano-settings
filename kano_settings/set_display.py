#!/usr/bin/env python

# set_display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano_settings.templates import TopBarTemplate, Template
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano.gtk3.heading import Heading
import kano_settings.constants as constants
from kano_settings.boot_config import set_config_comment
from kano.utils import run_cmd
from kano_settings.display.functions import get_model, list_supported_modes, set_hdmi_mode, read_hdmi_mode, \
    find_matching_mode, get_overscan_status, write_overscan_values, set_overscan_status
from kano_settings.data import get_data


class SetDisplay(Template):
    data = get_data("SET_DISPLAY")

    def __init__(self, win):
        title = self.data["LABEL_1"]
        kano_label = self.data["KANO_BUTTON"]

         # Get display name
        self.model = get_model()

        Template.__init__(self, title, self.model, kano_label)

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
        self.win.go_to_home()

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
        SetSimpleOverscan(self.win)


class OverscanTemplate(TopBarTemplate):
    overscan_pipe = "/var/tmp/overscan"
    data = get_data("SET_OVERSCAN")

    def __init__(self, win, title, description):
        TopBarTemplate.__init__(self)

        kano_label = self.data["KANO_BUTTON"]
        self.kano_button = KanoButton(kano_label)
        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.pack_and_align()

        self.heading = Heading(title, description)
        self.pack_start(self.heading.container, False, False, 0)

        self.win = win
        self.win.set_main_widget(self)

        self.top_bar.enable_prev()

        # Launch pipeline
        if not os.path.exists(self.overscan_pipe):
            run_cmd('mknod {} c 100 0'.format(self.overscan_pipe))

        self.overscan_values = get_overscan_status()
        self.original_overscan = get_overscan_status()

        # Reset button
        self.reset_button = OrangeButton()
        reset_image = Gtk.Image().new_from_file(constants.media + "/Icons/reset.png")
        self.reset_button.set_image(reset_image)
        self.reset_button.connect("button_press_event", self.reset)

    def apply_changes(self, button, event):
        # Apply changes
        write_overscan_values(self.overscan_values)
        set_config_comment('kano_screen_used', get_model())

        # Tell user to reboot to see changes
        constants.need_reboot = True

        self.go_to_display()

    def adjust(self, adj, varname):
        self.overscan_values[varname] = int(adj.get_value())
        set_overscan_status(self.overscan_values)

    def adjust_all(self, adj):
        self.overscan_values['top'] = int(adj.get_value())
        self.overscan_values['bottom'] = int(adj.get_value())
        self.overscan_values['left'] = int(adj.get_value())
        self.overscan_values['right'] = int(adj.get_value())
        set_overscan_status(self.overscan_values)

    def go_to_display(self, widget=None, button=None):
        self.win.clear_win()
        SetDisplay(self.win)

    def reset(self, widget=None, event=None):
        pass


class SetSimpleOverscan(OverscanTemplate):
    data_simple = get_data("SET_OVERSCAN_SIMPLE")

    def __init__(self, win):
        title = self.data_simple["LABEL_1"]
        description = self.data_simple["LABEL_2"]
        OverscanTemplate.__init__(self, win, title, description)

        self.top_bar.set_prev_callback(self.go_to_display)

        # Listen for key events
        self.key_press_handler = self.win.connect("key-press-event", self.on_key_press)

        ## slider
        self.t_scale = Gtk.HScale.new_with_range(0, 100, 1)
        self.t_scale.set_value(self.overscan_values['top'])
        self.t_scale.set_size_request(400, 30)
        self.t_scale.connect('value_changed', self.adjust_all)
        self.t_scale.set_value_pos(Gtk.PositionType.RIGHT)

        box = Gtk.Box()
        box.pack_start(self.t_scale, False, False, 0)
        box.pack_start(self.reset_button, False, False, 0)

        align = Gtk.Alignment(xalign=0.5, xscale=0, yscale=0, yalign=0.5)
        align.add(box)

        # Advance button
        self.advanced_button = OrangeButton()
        self.advanced_button.connect("button_press_event", self.go_to_advanced)
        self.advanced_button.set_label("Advanced")

        button_box = Gtk.ButtonBox()
        button_box.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        button_box.pack_start(self.advanced_button, False, False, 15)
        button_box.pack_start(self.kano_button.align, False, False, 15)
        empty_label = Gtk.Label(" ")
        button_box.pack_start(empty_label, False, False, 0)

        self.pack_start(align, True, True, 0)
        self.pack_end(button_box, False, False, 30)

        self.win.show_all()

    def reset(self, widget=None, event=None):
        # Restore overscan if any
        if self.original_overscan != self.overscan_values:
            set_overscan_status(self.original_overscan)
            self.t_scale.set_value(self.original_overscan['top'])

    def go_to_advanced(self, event=None, arg=None):
        # Remove key press handler from screen
        self.win.disconnect(self.key_press_handler)
        self.win.clear_win()
        SetAdvancedOverscan(self.win)

    def on_key_press(self, widget, event):
        # Right arrow (65363)
        if not hasattr(event, 'keyval') or event.keyval == 65363:
            self.overscan_values['top'] += 1
            self.overscan_values['bottom'] += 1
            self.overscan_values['left'] += 1
            self.overscan_values['right'] += 1
            set_overscan_status(self.overscan_values)
            self.t_scale.set_value(self.overscan_values['top'])
            return
         # Left arrow (65361)
        if not hasattr(event, 'keyval') or event.keyval == 65361:
            self.overscan_values['top'] -= 1
            self.overscan_values['bottom'] -= 1
            self.overscan_values['left'] -= 1
            self.overscan_values['right'] -= 1
            set_overscan_status(self.overscan_values)
            self.t_scale.set_value(self.overscan_values['top'])
            return


class SetAdvancedOverscan(OverscanTemplate):
    data_advanced = get_data("SET_OVERSCAN_ADVANCED")

    def __init__(self, win):
        title = self.data_advanced["LABEL_1"]
        description = self.data_advanced["LABEL_2"]
        OverscanTemplate.__init__(self, win, title, description)

        self.top_bar.set_prev_callback(self.go_to_simple_overscan)

        # Add sliders
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        ## Top slider
        self.t_scale = Gtk.HScale.new_with_range(0, 100, 1)
        self.t_scale.set_value(self.overscan_values['top'])
        self.t_scale.set_size_request(400, 30)
        self.t_scale.connect('value_changed', self.adjust, 'top')
        self.t_scale.set_value_pos(Gtk.PositionType.RIGHT)
        grid.attach(self.t_scale, 1, 0, 1, 1)
        top_label = Gtk.Label()
        top_label.set_alignment(xalign=1, yalign=1)
        top_label.set_text('Top')
        grid.attach(top_label, 0, 0, 1, 1)
        ## Bottom slider
        self.b_scale = Gtk.HScale.new_with_range(0, 100, 1)
        self.b_scale.set_value(self.overscan_values['bottom'])
        self.b_scale.set_size_request(400, 30)
        self.b_scale.connect('value_changed', self.adjust, 'bottom')
        self.b_scale.set_value_pos(Gtk.PositionType.RIGHT)
        grid.attach(self.b_scale, 1, 1, 1, 1)
        bottom_label = Gtk.Label()
        bottom_label.set_alignment(xalign=1, yalign=1)
        bottom_label.set_text('Bottom')
        grid.attach(bottom_label, 0, 1, 1, 1)
        ## Left slider
        self.l_scale = Gtk.HScale.new_with_range(0, 100, 1)
        self.l_scale.set_value(self.overscan_values['left'])
        self.l_scale.set_size_request(400, 30)
        self.l_scale.connect('value_changed', self.adjust, 'left')
        self.l_scale.set_value_pos(Gtk.PositionType.RIGHT)
        grid.attach(self.l_scale, 1, 2, 1, 1)
        left_label = Gtk.Label()
        left_label.set_alignment(xalign=1, yalign=1)
        left_label.set_text('Left')
        grid.attach(left_label, 0, 2, 1, 1)
        ## Right slider
        self.r_scale = Gtk.HScale.new_with_range(0, 100, 1)
        self.r_scale.set_value(self.overscan_values['right'])
        self.r_scale.set_size_request(400, 30)
        self.r_scale.connect('value_changed', self.adjust, 'right')
        self.r_scale.set_value_pos(Gtk.PositionType.RIGHT)
        grid.attach(self.r_scale, 1, 3, 1, 1)
        right_label = Gtk.Label()
        right_label.set_alignment(xalign=1, yalign=1)
        right_label.set_text('Right')
        grid.attach(right_label, 0, 3, 1, 1)

        align = Gtk.Alignment(xalign=0.5, xscale=0, yscale=0, yalign=0.5)
        align.add(grid)

        box = Gtk.Box()
        box.pack_start(align, True, True, 0)
        box.pack_start(self.reset_button, False, False, 0)

        self.pack_start(box, True, True, 0)
        self.pack_end(self.kano_button.align, False, False, 30)

        self.win.show_all()

    def reset(self, widget=None, event=None):
        # Restore overscan if any
        if self.original_overscan != self.overscan_values:
            set_overscan_status(self.original_overscan)
            self.t_scale.set_value(self.original_overscan['top'])
            self.b_scale.set_value(self.original_overscan['bottom'])
            self.l_scale.set_value(self.original_overscan['left'])
            self.r_scale.set_value(self.original_overscan['right'])

    def go_to_simple_overscan(self, widget, event):
        self.win.clear_win()
        SetSimpleOverscan()


