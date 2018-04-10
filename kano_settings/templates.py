#
# template.py
#
# Copyright (C) 2014 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Template container class
#

import os

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk

from kano.gtk3.buttons import KanoButton, OrangeButton
from kano_settings.components.heading import Heading
from kano.gtk3.scrolled_window import ScrolledWindow


class Template(Gtk.Box):

    def __init__(
        self,
        title,
        description,
        button_text,
        is_plug=False,
        back_btn=False
    ):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.title = Heading(title, description, is_plug, back_btn)
        self.title.container.set_margin_bottom(0)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.align = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.3)
        self.align.add(self.box)
        self.kano_button = KanoButton(button_text)
        self.kano_button.pack_and_align()
        self.kano_button.align.set_padding(0, 30, 0, 0)

        self.pack_start(self.title.container, False, False, 0)
        self.pack_start(self.align, True, True, 0)
        self.pack_end(self.kano_button.align, False, False, 0)

    def set_prev_callback(self, cb):
        self.title.set_prev_callback(cb)


class ScrolledWindowTemplate(Gtk.Box):

    def __init__(
        self,
        title,
        description,
        button_text,
        orange_button_text=None
    ):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.sw = ScrolledWindow()
        self.sw.apply_styling_to_widget(wide=False)

        self.title = Heading(title, description)
        self.kano_button = KanoButton(button_text)
        self.kano_button.pack_and_align()

        self.pack_start(self.title.container, False, False, 0)
        self.pack_start(self.sw, True, True, 0)

        if orange_button_text:
            box_align = Gtk.Alignment(xscale=0, xalign=0.5)
            button_box = Gtk.ButtonBox(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=40
            )

            label = Gtk.Label("")
            self.orange_button = OrangeButton(orange_button_text)
            button_box.pack_start(label, False, False, 0)
            button_box.pack_start(self.kano_button.align, False, False, 0)
            button_box.pack_start(self.orange_button, False, False, 0)

            box_align.add(button_box)
            self.pack_start(box_align, False, False, 0)
        else:
            self.pack_start(self.kano_button.align, False, False, 0)

    def get_scrolled_window(self):
        return self.sw


class LabelledListTemplate(Template):
    @staticmethod
    def label_button(button, text0, text1):
        button.set_label(text0)
        button.get_style_context().add_class('bold_toggle')

        info = Gtk.Label(text1)
        info.get_style_context().add_class('normal_label')

        box = Gtk.Box()
        box.pack_start(button, False, False, 0)
        box.pack_start(info, False, False, 0)

        return box

    def __init__(self, title, description, button_text, text_array):
        Template.__init__(self, title, description, button_text)
        self.button_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.buttons = []
        self.box.pack_start(self.button_container, False, False, 0)

    def label_button_and_pack(self, button, text0, text1):
        box = self.label_button(button, text0, text1)
        self.button_container.pack_start(box, False, False, 5)

    def get_button(self, index):
        return self.buttons[index]

    def set_button_spacing(self, number):
        self.button_container.set_spacing(number)


class RadioButtonTemplate(LabelledListTemplate):

    def __init__(self, title, description, button_text, text_array):
        LabelledListTemplate.__init__(self, title, description, button_text, text_array)

        for i in range(len(text_array)):
            if i == 0:
                button = Gtk.RadioButton.new_with_label_from_widget(None, text_array[0][0])
            else:
                button = Gtk.RadioButton.new_from_widget(self.buttons[0])
            self.buttons.append(button)
            self.label_button_and_pack(button, text_array[i][0], text_array[i][1])
            button.connect('toggled', self.on_button_toggled, i)

    def on_button_toggled(self, widget=None, selected=0):
        pass


class CheckButtonTemplate(LabelledListTemplate):

    def __init__(self, title, description, button_text, text_array):
        LabelledListTemplate.__init__(self, title, description, button_text, text_array)

        for text in text_array:
            button = Gtk.CheckButton()
            self.buttons.append(button)
            self.label_button_and_pack(button, text[0], text[1])


class EditableList(Gtk.Grid):

    def __init__(self, size_x=400, size_y=150):
        Gtk.Grid.__init__(self)

        self.set_row_spacing(10)
        self.set_column_spacing(10)

        scroll = ScrolledWindow()
        scroll.set_size_request(size_x, size_y)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.edit_list_store = Gtk.ListStore(str)
        self.edit_list = Gtk.TreeView(self.edit_list_store)
        self.edit_list.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect('edited', self._item_edited_handler)
        renderer.connect('editing-started', self._item_edit_started)
        renderer.connect('editing-canceled', self._item_edit_canceled)
        column = Gtk.TreeViewColumn(cell_renderer=renderer, text=0)
        self.edit_list.append_column(column)

        self._add_btn = KanoButton(_("ADD"))
        self._add_btn.connect('button-release-event', self.add)
        self._rm_btn = KanoButton(_("REMOVE"))
        self._set_rm_btn_state()
        self._rm_btn.connect('button-release-event', self.rm)

        scroll.add_with_viewport(self.edit_list)

        self.attach(scroll, 0, 0, 2, 1)
        self.attach(self._add_btn, 0, 1, 1, 1)
        self.attach(self._rm_btn, 1, 1, 1, 1)

    def __contains__(self, item):
        return item in [row[0] for row in self.edit_list_store]

    def add(self, button, event):
        self.edit_list_store.append([''])

        self.edit_list.grab_focus()

        row = len(self.edit_list_store) - 1
        col = self.edit_list.get_column(0)
        self.edit_list.set_cursor(row, col, start_editing=True)
        self._rm_btn.set_sensitive(False)

    def rm(self, button=None, event=None):
        selection = self.edit_list.get_selection()
        dummy, selected = selection.get_selected()

        if not selected:
            return

        self.edit_list_store.remove(selected)
        self._set_rm_btn_state()

    def _item_edited_handler(self, cellrenderertext, path, new_text):
        if new_text is None:
            # FIXME: the reason for the os.system here is that the 'edited' signal
            # triggers on a key-pressed-event and the dialog closes on release. So
            # you would only see the dialog while holding down the 'ENTER' key.
            title = _("Invalid website given")
            description = _("\nWe need to make sure the website URL is valid.\n" \
                            "Please enter the full URL as it appears in your browser.\n\n" \
                            "Example: http://www.google.com\n")
            buttons = _("OK:red:1")
            cmd = 'kano-dialog title="{}" description="{}" buttons="{}" no-taskbar &'.format(
                  title.encode('utf8'), description.encode('utf8'), buttons.encode('utf8'))
            os.system(cmd)
            self.rm()

        else:
            selection = self.edit_list.get_selection()
            dummy, selected = selection.get_selected()

            if new_text and new_text not in self:
                self.edit_list_store.set_value(selected, 0, new_text)
            else:
                row = self.edit_list_store[selected]
                old_text = row[0]

                if not old_text:
                    self.rm()

        self._add_btn.set_sensitive(True)
        self._set_rm_btn_state()

    def _item_edit_started(self, *_):
        self._add_btn.set_sensitive(False)

    def _item_edit_canceled(self, *_):
        self._add_btn.set_sensitive(True)
        self.rm()

    def _set_rm_btn_state(self):
        state = len(self.edit_list_store) != 0

        self._rm_btn.set_sensitive(state)


class TwoButtonTemplate(Gtk.Box):
    def __init__(self, title, description, left_btn_text, right_btn_text, buttons_shown):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.title = Heading(title, description)
        self.title.container.set_margin_bottom(0)

        self.sw = ScrolledWindow()
        self.sw.apply_styling_to_widget(wide=False)

        self.left_button = KanoButton(left_btn_text, color='orange')
        self.right_button = KanoButton(right_btn_text, color='green')

        kano_button_box = Gtk.ButtonBox()
        kano_button_box.set_layout(Gtk.ButtonBoxStyle.CENTER)
        kano_button_box.set_spacing(20)

        if buttons_shown == 2:
            kano_button_box.pack_start(self.left_button, False, False, 0)

        kano_button_box.pack_start(self.right_button, False, False, 0)

        self.pack_start(self.title.container, False, False, 0)
        self.pack_start(self.sw, True, True, 0)
        self.pack_end(kano_button_box, False, False, 0)

    def get_right_button(self):
        return self.right_button

    def get_left_button(self):
        return self.left_button
