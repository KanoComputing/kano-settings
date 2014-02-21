#!/usr/bin/env python3

# http://python-gtk-3-tutorial.readthedocs.org/en/latest/layout.html

from gi.repository import Gtk
import set_intro
import set_email
import set_keyboard
import set_audio
import set_display
import set_wifi

win = None
MAX_STATE = 6


# Window class
class MainWindow(Gtk.Window):
    table = None
    box = None
    state = 0

    def __init__(self):
        global table, box

        # Create main window
        Gtk.Window.__init__(self, title="Kano-Settings")
        self.set_size_request(450, 550)
        # Create common elements
        # Main table
        self.table = Gtk.Table(3, 3, True)
        self.add(self.table)
        # Title
        label = Gtk.Label()
        label.set_text("Kano Settings")
        label.set_justify(Gtk.Justification.LEFT)
        self.table.attach(label, 0, 3, 0, 1)

        # Prev Button
        bPrev = Gtk.Button(label="Previous", halign=Gtk.Align.START)
        bPrev.connect("clicked", self.on_prev)
        self.table.attach(bPrev, 0, 1, 2, 3)
        # Next button
        bNext = Gtk.Button(label="Next", halign=Gtk.Align.END)
        bNext.connect("clicked", self.on_next)
        self.table.attach(bNext, 2, 3, 2, 3)
        # Dynamic box
        self.box = Gtk.Box(spacing=6)
        self.table.attach(self.box, 0, 3, 1, 2)
        # Init
        set_intro.activate(self, self.table, self.box)

    def on_next(self, widget):
        global table, box, state

        # Remove element in the dynamic box
        for i in self.box.get_children():
            self.box.remove(i)
        # Update current state
        self.state = (self.state + 1) % MAX_STATE
        # Call next state
        self.state_to_widget(self.state).activate(self, self.table, self.box)
        # Refresh window
        win.show_all()

    def on_prev(self, widget):
        # Remove element in the dynamic box
        for i in self.box.get_children():
            self.box.remove(i)
        # Update current state
        self.state = (self.state - 1) % MAX_STATE
        # Call next state
        self.state_to_widget(self.state).activate(self, self.table, self.box)
        # Refresh window
        win.show_all()

    def state_to_widget(self, x):
        return {
            0: set_intro,
            1: set_email,
            2: set_keyboard,
            3: set_audio,
            4: set_display,
            5: set_wifi,
        }[x]


def main():
    global win

    # Create windown
    win = MainWindow()
    # Link delete event
    win.connect("delete-event", Gtk.main_quit)
    # Display window
    win.show_all()

    # start the GTK+ processing loop
    Gtk.main()

if __name__ == "__main__":
    # Print system python version for debugging purposes only
    print(str(Gtk.get_major_version()) + "." + str(Gtk.get_minor_version()) + "." + str(Gtk.get_micro_version()))

    main()
