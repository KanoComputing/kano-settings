#!/usr/bin/env python3

# http://python-gtk-3-tutorial.readthedocs.org/en/latest/layout.html

from gi.repository import Gtk, Gdk,GdkPixbuf, Pango
import set_intro
import set_email
import set_keyboard
import set_audio
import set_display
import set_wifi
import dialog_box

win = None
MAX_STATE = 6


# Window class
class MainWindow(Gtk.Window):
    grid = None
    box = None
    state = 0

    def __init__(self):
        global grid, box

        # Create main window
        Gtk.Window.__init__(self, title="Kano-Settings")
        # Remove decoration
        self.set_decorated(False)

        self.set_size_request(450, 600)

        self.new_grid = Gtk.Grid()

        self.top_bar_container = Gtk.EventBox()
        self.top_bar_container.set_size_request(450, 60)

        top_bar_container_style = self.top_bar_container.get_style_context()
        top_bar_container_style.add_class('top_bar_container')

        header_title = Gtk.Label("TITLE")
        header_title.props.halign = Gtk.Align.CENTER
        header_title.modify_font(Pango.FontDescription("Bariol 15"))

        title = Gtk.Label("TITLE")
        title.modify_font(Pango.FontDescription("Bariol 18"))
        description = Gtk.Label("Description of project")
        description.modify_font(Pango.FontDescription("Bariol 18"))

        title_style = title.get_style_context()
        title_style.add_class('title')

        description_style = description.get_style_context()
        description_style.add_class('description')

        self.top_bar = Gtk.Box()
        self.top_bar.set_homogeneous(False)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("media/Kano-BlockplatformIcons.png", 648, 24)
        icons = []
        images = []

        for x in range(int(648/24)):
            subpixel = pixbuf.new_subpixbuf(24*x, 0, 24, 24).add_alpha(True,255,255,255)
            icons.append(subpixel)
            images.append(Gtk.Image())
            images[x].set_from_pixbuf(icons[x])

        # Title
        label = Gtk.Label()
        label.set_text("Kano Settings")
        label.set_justify(Gtk.Justification.LEFT)
        self.new_grid.attach(label, 0, 3, 0, 1)

        # Prev Button
        #bPrev = Gtk.Button(label="Previous", halign=Gtk.Align.START)
        prev_button = Gtk.Button()
        prev_button.set_image(images[0])
        prev_button.set_size_request(60, 60)
        prev_button.connect("clicked", self.on_prev)

        # Next button
        next_button = Gtk.Button()
        next_button.set_image(images[3])
        next_button.set_size_request(60, 60)
        next_button.connect("clicked", self.on_next)

        close_button = Gtk.Button()
        close_button.set_image(images[15])
        close_button.set_size_request(60, 60)
        close_button.connect("clicked", Gtk.main_quit)

        # Dynamic box
        self.grid = Gtk.Grid()
        self.box = Gtk.Box(spacing=6)
        self.box.props.halign = Gtk.Align.CENTER
        self.grid.attach(self.box, 0, 3, 1, 2)
        self.grid.set_size_request(450, 300)
        self.grid.props.halign = Gtk.Align.CENTER

        """main_part = Gtk.Grid()
                                img = Gtk.Image()
                                img.set_from_file("media/Judoka-Error.png")
                                main_part.add(img)
                                main_part.props.halign = Gtk.Align.CENTER"""

        # Init
        set_intro.activate(self, self.grid, self.box)

        title_container = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=0)
        title_container.add(title)
        title_container.set_size_request(300, 100)
        title_container.pack_start(description, True, True, 10)
        info_style = title_container.get_style_context()
        info_style.add_class('info')

        apply_changes_text = Gtk.Label("Next")
        apply_changes = Gtk.Button()
        apply_changes.props.halign = Gtk.Align.CENTER
        apply_changes.set_size_request(70, 30)
        apply_changes_label = Gtk.Box()
        apply_changes_label.pack_start(images[5], False, False, 2)
        apply_changes_label.pack_start(apply_changes_text, False, False, 2)
        
        apply_changes.add(apply_changes_label)
        apply_changes_text.modify_font(Pango.FontDescription("Bariol 14"))

        next_button_style = apply_changes.get_style_context()
        next_button_style.add_class('apply_changes')

        self.top_bar.add(prev_button)
        self.top_bar.pack_start(next_button, False, False, 0)
        self.top_bar.pack_start(header_title, True, True, 200)
        self.top_bar.pack_end(close_button, False, False, 0)
        self.top_bar_container.add(self.top_bar)
        self.new_grid.attach(self.top_bar_container, 0, 0, 1, 1)
        self.new_grid.attach(title_container, 0, 1, 1, 1)
        self.new_grid.attach(self.grid, 0, 2, 1, 1)
        self.new_grid.attach(apply_changes, 0, 3, 1, 1)
        self.add(self.new_grid)

    def on_next(self, widget):
        global grid, box, state

        # Remove element in the dynamic box
        for i in self.box.get_children():
            self.box.remove(i)
        # Update current state
        self.state = (self.state + 1) % MAX_STATE
        # Call next state
        self.state_to_widget(self.state).activate(self, self.grid, self.box)
        # Refresh window
        win.show_all()

    def on_prev(self, widget):
        # Remove element in the dynamic box
        for i in self.box.get_children():
            self.box.remove(i)
        # Update current state
        self.state = (self.state - 1) % MAX_STATE
        # Call next state
        self.state_to_widget(self.state).activate(self, self.grid, self.box)
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
    # Create style sheet
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path('style.css')
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider,
                                     Gtk.STYLE_PROVIDER_PRIORITY_USER)

    # Create windown
    win = MainWindow()
    # Link delete event
    win.connect("delete-event", close_window)
    # Display window
    win.show_all()

    # start the GTK+ processing loop
    Gtk.main()

def close_window(arg1, arg2):
    print(arg1)
    print(arg2)
    print("set_audio.reboot = " + str(set_audio.reboot))
    if set_audio.reboot or set_display.reboot:
        dialog = Gtk.Dialog()
        reboot_message = dialog_box.DialogWindow(dialog, "Some of the changes you made will only take place after a reboot.")
        response = reboot_message.run()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
            reboot_message.destroy() 
            Gtk.main_quit()
            return

    else:
        Gtk.main_quit()

    

if __name__ == "__main__":
    # Print system python version for debugging purposes only
    print(str(Gtk.get_major_version()) + "." + str(Gtk.get_minor_version()) + "." + str(Gtk.get_micro_version()))

    main()
