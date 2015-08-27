#!/usr/bin/env python

# set_display.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk
from kano_settings.templates import Template
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano.gtk3.kano_combobox import KanoComboBox
from kano_settings.components.heading import Heading
from kano_profile.tracker import track_data

import kano_settings.common as common
from kano_settings.boot_config import set_config_comment
from kano_settings.system.display import get_model, get_status, list_supported_modes, set_hdmi_mode, read_hdmi_mode, \
    find_matching_mode, get_overscan_status, write_overscan_values, set_overscan_status, launch_pipe


class SetDisplay(Template):
    def __init__(self, win):
        # Show the Display brand and model
        self.model = get_model()
        info_message = ' (Changing this requires a reboot)'

        # And the current display resolution
        try:
            current_resolution = get_status()['resolution']
            info_message += '\n\nCurrent resolution: {}'.format(current_resolution)
        except:
            pass

        Template.__init__(
            self,
            "Display",
            self.model + info_message,
            "APPLY CHANGES"
        )

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self.kano_button.set_sensitive(False)
        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.connect("key-release-event", self.apply_changes)

        horizontal_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
        horizontal_container.set_valign(Gtk.Align.CENTER)

        # HDMI mode combo box
        self.mode_combo = KanoComboBox(max_display_items=7)
        self.mode_combo.connect("changed", self.on_mode_changed)

        # Fill list of modes
        modes = list_supported_modes()
        self.mode_combo.append("auto")
        if modes:
            for v in modes:
                self.mode_combo.append(v)

        horizontal_container.pack_start(self.mode_combo, False, False, 0)
        self.mode_combo.props.valign = Gtk.Align.CENTER

        # Select the current setting in the dropdown list
        saved_group, saved_mode = read_hdmi_mode()
        active_item = find_matching_mode(modes, saved_group, saved_mode)
        self.mode_combo.set_selected_item_index(active_item)
        self.init_item = active_item
        # Overscan button
        overscan_button = OrangeButton("Overscan")
        horizontal_container.pack_end(overscan_button, False, False, 0)
        overscan_button.connect("button-release-event", self.go_to_overscan)

        self.box.pack_start(horizontal_container, False, False, 0)

        # Add apply changes button under the main settings content
        self.win.show_all()

    def apply_changes(self, button, event):

        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Return:

            # Check if we have done any change
            if self.init_item != self.mode_index:
                # Set HDMI mode
                # Get mode:group string
                # Of the form "auto" or "cea:1" or "dmt:1" etc.
                parse_mode = self.mode.split(" ")[0]
                self.set_hdmi_mode_from_str(parse_mode)

                # Track the user's screen resolution
                track_data("screen-mode-changed", {
                    "mode": parse_mode
                })

                common.need_reboot = True

            self.win.go_to_home()

    def on_mode_changed(self, combo):

        #  Get the selected mode
        self.mode = combo.get_selected_item_text()
        self.mode_index = combo.get_selected_item_index()

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
        # Check if overscan values are all the same
        overscan_values = get_overscan_status()
        if overscan_values['top'] != overscan_values['bottom'] or \
           overscan_values['top'] != overscan_values['left'] or \
           overscan_values['top'] != overscan_values['right']:
            SetAdvancedOverscan(self.win, overscan_values)
        else:
            SetSimpleOverscan(self.win, overscan_values)


class OverscanTemplate(Gtk.Box):
    def __init__(self, win, title, description, original_overscan=None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.kano_button = KanoButton("APPLY CHANGES")
        self.kano_button.connect("button-release-event", self.apply_changes)
        self.kano_button.pack_and_align()

        self.heading = Heading(title, description)
        self.pack_start(self.heading.container, False, False, 0)

        self.win = win
        self.win.set_main_widget(self)

        self.win.top_bar.enable_prev()

        # Launch pipe for the overscan c code
        launch_pipe()

        self.overscan_values = get_overscan_status()
        self.original_overscan = original_overscan

        # Pass original overscan values between the classes
        # If original_overscan hasn't been generated yet, get it from current overscan status
        # Alternatively, maybe read this from a file in future
        if original_overscan is None:
            self.original_overscan = get_overscan_status()

        # Reset button
        self.reset_button = OrangeButton()
        reset_image = Gtk.Image().new_from_file(common.media + "/Icons/reset.png")
        self.reset_button.set_image(reset_image)
        self.reset_button.connect("button_press_event", self.reset)

    def apply_changes(self, button, event):
        # Apply changes
        write_overscan_values(self.overscan_values)
        self.original_overscan = self.overscan_values
        set_config_comment('kano_screen_used', get_model())

        # Tell user to reboot to see changes
        common.need_reboot = True

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
        self.reset()
        self.win.clear_win()
        SetDisplay(self.win)

    def reset(self, widget=None, event=None):
        pass


class SetSimpleOverscan(OverscanTemplate):
    def __init__(self, win, original_overscan=None):
        OverscanTemplate.__init__(
            self,
            win,
            "Overscan",
            "This setting lets you adjust your screen's size.",
            original_overscan
        )

        self.win.change_prev_callback(self.go_to_display)

        # Listen for key events
        self.key_press_handler = self.win.connect("key-press-event", self.on_key_press)

        ## slider
        self.t_value = Gtk.Label()
        self.t_value.get_style_context().add_class("slider_label")
        self.t_scale = Gtk.HScale.new_with_range(0, 100, 1)
        self.t_scale.set_value(self.overscan_values['top'])
        self.t_scale.set_size_request(400, 30)
        self.t_scale.connect('value_changed', self.adjust_all)
        self.t_scale.connect('value_changed', self.update_all_values)
        self.t_scale.set_draw_value(False)
        self.update_all_values(self.t_scale)

        box = Gtk.Box()
        box.pack_start(self.t_scale, False, False, 5)
        box.pack_start(self.t_value, False, False, 5)
        box.pack_start(self.reset_button, False, False, 25)

        align = Gtk.Alignment(xalign=0.6, xscale=0, yscale=0, yalign=0.5)
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
        SetAdvancedOverscan(self.win, self.original_overscan)

    def on_key_press(self, widget, event):
        # Right arrow (65363)
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Right:
            self.overscan_values['top'] += 1
            self.overscan_values['bottom'] += 1
            self.overscan_values['left'] += 1
            self.overscan_values['right'] += 1
            set_overscan_status(self.overscan_values)
            self.t_scale.set_value(self.overscan_values['top'])
            return
         # Left arrow (65361)
        if not hasattr(event, 'keyval') or event.keyval == Gdk.KEY_Left:
            self.overscan_values['top'] -= 1
            self.overscan_values['bottom'] -= 1
            self.overscan_values['left'] -= 1
            self.overscan_values['right'] -= 1
            set_overscan_status(self.overscan_values)
            self.t_scale.set_value(self.overscan_values['top'])
            return

    def update_all_values(self, widget):
        new_value = str(int(widget.get_value()))
        self.t_value.set_text(new_value)


class SetAdvancedOverscan(OverscanTemplate):
    def __init__(self, win, original_overscan):
        OverscanTemplate.__init__(
            self,
            win,
            "Overscan",
            "This setting lets you adjust your screen's size, edge by edge.",
            original_overscan
        )

        self.win.change_prev_callback(self.go_to_display)

        # Add sliders
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(15)

        # Labels next to sliders
        self.t_value = Gtk.Label()
        self.b_value = Gtk.Label()
        self.l_value = Gtk.Label()
        self.r_value = Gtk.Label()

        ## Top slider
        t_value, self.t_scale, top_label = self.generate_slider_label('top')
        grid.attach(self.t_scale, 1, 0, 1, 1)
        grid.attach(top_label, 0, 0, 1, 1)
        grid.attach(t_value, 2, 0, 1, 1)

        ## Bottom slider
        b_value, self.b_scale, bottom_label = self.generate_slider_label('bottom')
        grid.attach(self.b_scale, 1, 1, 1, 1)
        grid.attach(bottom_label, 0, 1, 1, 1)
        grid.attach(b_value, 2, 1, 1, 1)

        ## Left slider
        l_value, self.l_scale, left_label = self.generate_slider_label('left')
        grid.attach(self.l_scale, 1, 2, 1, 1)
        grid.attach(left_label, 0, 2, 1, 1)
        grid.attach(l_value, 2, 2, 1, 1)

        ## Right slider
        r_value, self.r_scale, right_label = self.generate_slider_label('right')
        grid.attach(right_label, 0, 3, 1, 1)
        grid.attach(self.r_scale, 1, 3, 1, 1)
        grid.attach(r_value, 2, 3, 1, 1)

        box = Gtk.Box()
        box.pack_start(grid, False, False, 0)
        box.pack_start(self.reset_button, False, False, 25)

        align = Gtk.Alignment(xalign=0.6, xscale=0, yscale=0, yalign=0.5)
        align.add(box)

        self.pack_start(align, True, True, 0)
        self.pack_end(self.kano_button.align, False, False, 30)

        self.win.show_all()

    # direction = 'top', 'bottom', 'right', 'left'
    def generate_slider_label(self, direction):
        value_label = Gtk.Label()
        value_label.get_style_context().add_class("slider_label")
        slider = Gtk.HScale.new_with_range(0, 100, 1)
        slider.set_value(self.overscan_values[direction])
        slider.set_size_request(400, 30)
        slider.connect('value_changed', self.adjust, direction)
        slider.connect('value_changed', self.update_value, value_label)
        slider.set_value_pos(Gtk.PositionType.RIGHT)
        slider.set_draw_value(False)
        dir_label = Gtk.Label()
        dir_label.get_style_context().add_class("slider_label")
        dir_label.set_alignment(xalign=1, yalign=1)
        dir_label.set_text(direction.title())
        self.update_value(slider, value_label)
        return value_label, slider, dir_label

    def reset(self, widget=None, event=None):
        # Restore overscan if any
        if self.original_overscan != self.overscan_values:
            set_overscan_status(self.original_overscan)
            self.t_scale.set_value(self.original_overscan['top'])
            self.b_scale.set_value(self.original_overscan['bottom'])
            self.l_scale.set_value(self.original_overscan['left'])
            self.r_scale.set_value(self.original_overscan['right'])

    def update_value(self, widget, label):
        new_value = str(int(widget.get_value()))
        label.set_text(new_value)
