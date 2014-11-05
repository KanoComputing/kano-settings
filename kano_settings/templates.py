
#!/usr/bin/env python

# template.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Template container class
#

from gi.repository import Gtk

from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.scrolled_window import ScrolledWindow


class Template(Gtk.Box):

    def __init__(self, title, description, button_text):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.title = Heading(title, description)
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


class ScrolledWindowTemplate(Gtk.Box):

    def __init__(self, title, description, button_text):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.sw = ScrolledWindow(wide_scrollbar=True)
        self.sw.set_size_request(630, 210)
        self.title = Heading(title, description)
        self.kano_button = KanoButton(button_text)
        self.kano_button.pack_and_align()

        self.pack_start(self.title.container, False, False, 0)
        self.pack_start(self.sw, False, False, 0)
        self.pack_start(self.kano_button.align, False, False, 0)


class LabelledListTemplate(Template):
    @staticmethod
    def label_button(button, text0, text1):
        button.set_label(text0)
        button.get_style_context().add_class("bold_toggle")

        info = Gtk.Label(text1)
        info.get_style_context().add_class("normal_label")

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

        button = Gtk.RadioButton.new_with_label_from_widget(None, text_array[0][0])
        self.buttons.append(button)
        self.label_button_and_pack(button, text_array[0][0], text_array[0][1])
        text_array.remove(text_array[0])
        button.connect("toggled", self.on_button_toggled)

        for text in text_array:
            button = Gtk.RadioButton.new_from_widget(self.buttons[0])
            self.buttons.append(button)
            self.label_button_and_pack(button, text[0], text[1])
            button.connect("toggled", self.on_button_toggled)

    def on_button_toggled(self, widget=None):
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

        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(size_x, size_y)

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

        self._add_btn = Gtk.Button('ADD')
        self._add_btn.connect('button-release-event', self.add)
        self._rm_btn = Gtk.Button('REMOVE')
        self._rm_btn.connect('button-release-event', self.rm)

        scroll.add(self.edit_list)

        self.attach(scroll, 0, 0, 2, 1)
        self.attach(self._add_btn, 0, 1, 1, 1)
        self.attach(self._rm_btn, 1, 1, 1, 1)

    def add(self, button, event):
        self.edit_list_store.append([''])

        self.edit_list.grab_focus()

        row = len(self.edit_list_store) - 1
        col = self.edit_list.get_column(0)
        self.edit_list.set_cursor(row, col, start_editing=True)

    def rm(self, button=None, event=None):
        selection = self.edit_list.get_selection()
        _, selected = selection.get_selected()

        if not selected:
            return

        self.edit_list_store.remove(selected)

    def _item_edited_handler(self, cellrenderertext, path, new_text):
        selection = self.edit_list.get_selection()
        _, selected = selection.get_selected()

        if not new_text:
            row = self.edit_list_store[selected]
            old_text = row[0]

            if old_text:
                return

            self.rm()

        self.edit_list_store.set_value(selected, 0, new_text)
        self._add_btn.set_sensitive(True)

    def _item_edit_started(self, *_):
        self._add_btn.set_sensitive(False)

    def _item_edit_canceled(self, *_):
        self._add_btn.set_sensitive(True)
