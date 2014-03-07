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
import config_file

win = None
MAX_STATE = 6


# Window class
class MainWindow(Gtk.Window):
    grid = None
    box = None
    state = 0

    def __init__(self):
        global grid, box

        TOP_BAR_HEIGHT = 50
        WINDOW_WIDTH = 600
        WINDOW_HEIGHT = 380

        # Create main window
        Gtk.Window.__init__(self, title="Kano-Settings")
        # Remove decoration
        self.set_decorated(False)

        self.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Main container of the window
        self.grid = Gtk.Grid()

        # This is to give the correct colour of the top bar as Event Boxes are the only containers that we can colour
        self.top_bar_container = Gtk.EventBox()
        self.top_bar_container.set_size_request(WINDOW_WIDTH, TOP_BAR_HEIGHT)
        top_bar_container_style = self.top_bar_container.get_style_context()
        top_bar_container_style.add_class('top_bar_container')

        # Main title of he window bar.
        header = Gtk.Label("Kano Settings")
        header.props.halign = Gtk.Align.CENTER
        header.modify_font(Pango.FontDescription("Bariol 13"))
        header.get_style_context().add_class("header")

        self.top_bar = Gtk.Box()
        self.top_bar.set_homogeneous(False)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("media/Icons/systemsetup-icons.png", 192, 24)
        icons = []
        images = []

        for x in range(int(192/24)):
            subpixel = pixbuf.new_subpixbuf(24*x, 0, 24, 24).add_alpha(True,255,255,255)
            icons.append(subpixel)
            images.append(Gtk.Image())
            images[x].set_from_pixbuf(icons[x])

        # Prev Button
        #bPrev = Gtk.Button(label="Previous", halign=Gtk.Align.START)
        prev_button = Gtk.Button()
        prev_button.set_image(images[2])
        prev_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        prev_button.connect("clicked", self.on_prev)

        # Next button
        next_button = Gtk.Button()
        next_button.set_image(images[3])
        next_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        next_button.connect("clicked", self.on_next)

        close_button = Gtk.Button()
        close_button.set_image(images[6])
        close_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        close_button.connect("clicked", Gtk.main_quit)

        # Dynamic box

        #############################################################################
        # Move this into set_email etc (or separate file)
        # Needed for everything but intro screens.

        self.apply_changes_text = Gtk.Label("Next")
        self.apply_changes = Gtk.Button()
        self.apply_changes.props.halign = Gtk.Align.CENTER
        self.apply_changes.set_size_request(70, 30)
        self.apply_changes_label = Gtk.Box()
        self.apply_changes_label.pack_start(self.apply_changes_text, False, False, 2)
        self.apply_changes_label.pack_start(images[0], False, False, 2)
        self.apply_changes.add(self.apply_changes_label)
        self.apply_changes_text.modify_font(Pango.FontDescription("Bariol 14"))
        self.apply_changes.connect('clicked', self.update_and_next)

        next_button_style = self.apply_changes.get_style_context()
        next_button_style.add_class('apply_changes')

        #self.main_part = Gtk.Grid()
        #self.main_part.get_style_context().add_class("main_part")
        #self.main_part.set_size_request(WINDOW_WIDTH, 300)
        self.changable_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.changable_content.props.halign = Gtk.Align.CENTER
        #self.main_part.attach(self.changable_content, 0, 1, 1, 2)
        #self.main_part.props.halign = Gtk.Align.CENTER

        # Init
        if config_file.read_from_file('finished'):
            self.default_intro(self.title, self.description) #, self.main_part, self.changable_content, self.title, self.description)
        else:
            set_intro.activate(self, self.changable_content, self.apply_changes)

        self.top_bar.add(prev_button)
        self.top_bar.pack_start(next_button, False, False, 0)
        self.top_bar.pack_start(header, True, True, 0)
        self.top_bar.pack_end(close_button, False, False, 0)
        self.top_bar_container.add(self.top_bar)
        self.grid.attach(self.top_bar_container, 0, 0, 1, 1)

        self.grid.attach(self.changable_content, 0, 2, 1, 1)
        self.grid.set_row_spacing(0)

        self.add(self.grid)

    def default_intro(self, title, description):
        global grid, box, state

        # Read from config file.
        # If value is 1:
        table = Gtk.Table(3, 2, True)

        names = ["Email", "Keyboard", "Audio", "Display", "Wifi"]
        buttons = []
        label_styles = []

        for x in range(len(names)):
            label_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=0)
            button_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing=0)

            label = Gtk.Label(names[x])
            label.get_style_context().add_class("intro_label")
            label2 = Gtk.Label("Custom info")
            label2.get_style_context().add_class("custom_label")
            button = Gtk.Button()
            img = Gtk.Image()
            img.set_from_file("media/Icons/Icon-" + names[x] + ".png")

            label_box.pack_start(label, True, True, 0)
            label_box.pack_start(label2, True, True, 0)
            #label.set_justify(Gtk.Justification.LEFT)
            #label2.set_justify(Gtk.Justification.LEFT)

            button_box.pack_start(img, True, True, 0)
            button_box.pack_start(label_box, True, True, 5)
            button.add(button_box)
            buttons.append(button)
            button.state = x
            button.connect("clicked", self.go_to_level)

        # Attach to table
        table.attach(buttons[0], 0, 1, 0, 1, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        table.attach(buttons[1], 0, 1, 1, 2, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        table.attach(buttons[2], 0, 1, 2, 3, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        table.attach(buttons[3], 1, 2, 0, 1, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        table.attach(buttons[4], 1, 2, 1, 2, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)

        table.set_size_request(450, 100)

        self.changable_content.pack_start(table, True, True, 0)

    def update_and_next(self, widget):
        self.state_to_widget(self.state).apply_changes(widget)
        self.on_next(widget)

    def on_next(self, widget):
        global grid, box, state

        # Remove element in the dynamic box
        for i in self.changable_content.get_children():
            self.changable_content.remove(i)
        # Update current state
        self.state = (self.state + 1) % MAX_STATE
        # Call next state
        self.state_to_widget(self.state).activate(self, self.changable_content, self.apply_changes)
        # Refresh window
        win.show_all()

    def on_prev(self, widget):
        # Remove element in the dynamic box
        for i in self.changable_content.get_children():
            self.changable_content.remove(i)
        # Update current state
        self.state = (self.state - 1) % MAX_STATE
        # Call next state
        self.state_to_widget(self.state).activate(self, self.changable_content, self.apply_changes)
        # Refresh window
        win.show_all()

    def go_to_level(self, widget):
        # Remove element in the dynamic box
        for i in self.changable_content.get_children():
            self.changable_content.remove(i)
        # Update current state
        self.state = widget.state
        # Call next state
        self.state_to_widget(self.state).activate(self, self.changable_content, self.apply_changes)
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

    if set_audio.reboot or set_display.reboot:
        dialog = Gtk.Dialog()
        reboot_message = dialog_box.DialogWindow(dialog, "Some of the changes you made will only take place after a reboot.")
        response = reboot_message.run()

        if response == Gtk.ResponseType.OK:
            reboot_message.destroy() 
            Gtk.main_quit()
            return

    else:
        Gtk.main_quit()

    

if __name__ == "__main__":
    # Print system python version for debugging purposes only
    print(str(Gtk.get_major_version()) + "." + str(Gtk.get_minor_version()) + "." + str(Gtk.get_micro_version()))

    main()
