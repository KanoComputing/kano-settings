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
names = ["Email", "Keyboard", "Audio", "Wifi", "Display"]
custom_info = ["Email", "Keyboard-country-human", "Audio", "Wifi", "Display"]


# Window class
class MainWindow(Gtk.Window):
    grid = None
    box = None
    state = 0

    def __init__(self):
        global grid, box

        self.last_level_visited = 0

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
        prev_button.set_can_focus(False)

        # Next button
        next_button = Gtk.Button()
        next_button.set_image(images[3])
        next_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        next_button.set_can_focus(False)

        close_button = Gtk.Button()
        close_button.set_image(images[6])
        close_button.set_size_request(TOP_BAR_HEIGHT, TOP_BAR_HEIGHT)
        close_button.connect("clicked", Gtk.main_quit)
        close_button.set_can_focus(False)

        # Dynamic box

        #############################################################################
        # Move this into set_email etc (or separate file)
        # Needed for everything but intro screens.

        self.apply_changes_text = Gtk.Label("Get started")
        self.apply_changes = Gtk.Button()
        self.apply_changes.props.halign = Gtk.Align.CENTER
        self.apply_changes.set_size_request(70, 30)
        self.apply_changes_label = Gtk.Box()
        self.apply_changes_label.pack_start(self.apply_changes_text, False, False, 2)
        self.apply_changes_label.pack_start(images[0], False, False, 2)
        self.apply_changes.add(self.apply_changes_label)
        self.apply_changes_text.modify_font(Pango.FontDescription("Bariol bold 13"))
        self.apply_changes.connect('clicked', self.update_and_next)
        self.apply_changes.set_can_focus(False)

        next_button_style = self.apply_changes.get_style_context()
        next_button_style.add_class('apply_changes')

        self.changable_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.changable_content.props.halign = Gtk.Align.CENTER

        # Init
        if config_file.read_from_file('Completed') == "1":
            print("Settings has been completed before")
            self.default_intro = Gtk.Table(3, 2, True)
            self.default_intro_init()
            #Need new functions here
            next_button.connect("clicked", self.default_next)
            prev_button.connect("clicked", self.back_to_intro)
        else:
            print("Settings has NOT been completed before")
            set_intro.activate(self, self.changable_content, self.apply_changes)
            prev_button.connect("clicked", self.on_prev)
            next_button.connect("clicked", self.on_next)

        self.top_bar.add(prev_button)
        self.top_bar.pack_start(next_button, False, False, 0)
        self.top_bar.pack_start(header, True, True, 0)
        self.top_bar.pack_end(close_button, False, False, 0)
        self.top_bar_container.add(self.top_bar)
        self.grid.attach(self.top_bar_container, 0, 0, 1, 1)

        self.grid.attach(self.changable_content, 0, 2, 1, 1)
        self.grid.set_row_spacing(0)

        self.add(self.grid)


    def back_to_intro(self, arg2):
        # save last level?
        for i in self.changable_content.get_children():
            self.changable_content.remove(i)

        self.default_intro_text()

        self.changable_content.pack_start(self.default_intro, True, True, 0)


    def default_intro_init(self):
        global grid, box, state

        for i in self.changable_content.get_children():
            self.changable_content.remove(i)

        # Read from config file.
        # If value is 1:
        self.default_intro = Gtk.Table(3, 2, True)

        buttons = []
        self.labels = []

        #names at top of file
        for x in range(len(names)):
            label_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=0)
            button_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing=0)

            label = Gtk.Label(names[x])
            label.get_style_context().add_class("intro_label")

            print(custom_info[x])
            info = config_file.read_from_file(custom_info[x])

            if info != None:
                # Replace some of the info displayed with whitespace so it fits
                if len(info) >= 12:
                    info = info[0:12] + '...'

            label2 = Gtk.Label(info)
            label2.get_style_context().add_class("custom_label")
            self.labels.append(label2)
            button = Gtk.Button()
            button.set_can_focus(False)
            img = Gtk.Image()
            img.set_from_file("media/Icons/Icon-" + names[x] + ".png")

            label_box.pack_start(label, True, True, 0)
            label_box.pack_start(label2, True, True, 0)
            label_box.set_size_request(90,20)
            #label.set_justify(Gtk.Justification.LEFT)
            #label2.set_justify(Gtk.Justification.LEFT)

            button_box.pack_start(img, True, True, 10)
            button_box.pack_start(label_box, True, True, 0)
            button_box.set_size_request(180, 80)
            button.add(button_box)
            buttons.append(button)
            button.state = x
            button.set_size_request(200, 100)
            button.connect("clicked", self.go_to_level)

        # Attach to table
        self.default_intro.attach(buttons[0], 0, 1, 0, 1, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.default_intro.attach(buttons[1], 0, 1, 1, 2, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.default_intro.attach(buttons[2], 0, 1, 2, 3, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.default_intro.attach(buttons[3], 1, 2, 0, 1, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)
        self.default_intro.attach(buttons[4], 1, 2, 1, 2, Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 5, 5)

        self.default_intro.set_size_request(450, 100)

        self.changable_content.pack_start(self.default_intro, True, True, 0)


    def default_intro_text(self):
        for x in range(len(custom_info)):
            config_file.read_from_file(custom_info[x])
            self.labels[x].set_text(str(config_file.read_from_file(custom_info[x])))


    def update_and_next(self, widget):
        returnValue = self.state_to_widget(self.state).apply_changes(widget)
        if returnValue == -1:
            return

        self.on_next(widget)


    def default_next(self, widget):
        if self.last_level_visited == 0:
            return

        for i in self.changable_content.get_children():
            self.changable_content.remove(i)

        
        self.state_to_widget(self.last_level_visited).activate(self, self.changable_content, self.apply_changes) 
        self.last_level_visited = self.state   
        win.show_all()

    def on_next(self, widget):
        global grid, box, state

        # Update current state
        self.state = (self.state + 1)
        # If we've clicked on the finished
        if self.state == MAX_STATE:
            # Write to config file to say we've completed the level.
            config_file.replace_setting("Completed", "1")
            # Finished, so close window
            close_window()
            return

        # Remove element in the dynamic box
        for i in self.changable_content.get_children():
            self.changable_content.remove(i)

        # Call next state
        self.state_to_widget(self.state).activate(self, self.changable_content, self.apply_changes)

        # Change label on Apply Changes button
        if self.state == MAX_STATE -1:
            self.apply_changes_text.set_text("Finish!")
        elif self.state > 0:
            self.apply_changes_text.set_text("Next")
        else:
            self.apply_changes_text.set_text("Get started")
        # Refresh window
        win.show_all()

    def on_prev(self, widget):
         # Update current state
        self.state = (self.state - 1)
        # Check we're in a valid state
        if self.state == -1:
            self.state = 0
            return;

        # Remove element in the dynamic box
        for i in self.changable_content.get_children():
            self.changable_content.remove(i)
       
        # Call next state
        self.state_to_widget(self.state).activate(self, self.changable_content, self.apply_changes)

        # Change label on Apply Changes button
        if self.state == MAX_STATE -1:
            self.apply_changes_text.set_text("Finish!")
        elif self.state > 0:
            self.apply_changes_text.set_text("Next")
        else:
            self.apply_changes_text.set_text("Get started")
        # Refresh window
        win.show_all()

    def go_to_level(self, widget):
        # Remove element in the dynamic box
        for i in self.changable_content.get_children():
            self.changable_content.remove(i)
        # Update current state
        self.state = widget.state + 1
        # Record this level so we can go back to it
        self.last_level_visited = self.state
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
            4: set_wifi,
            5: set_display,
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

def close_window(event="delete-event", button=win):

    if set_audio.reboot or set_display.reboot:
        #Bring in message dialog box
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "This is an INFO MessageDialog")
        dialog.format_secondary_text(
            "And this is the secondary text that explains things.")
        dialog.run()
        print("INFO dialog closed")

        if response == Gtk.ResponseType.OK:
            dialog.destroy() 
            Gtk.main_quit()
            return
        else:
            dialog.destroy()

    else:
        Gtk.main_quit()


if __name__ == "__main__":
    # Print system python version for debugging purposes only
    print(str(Gtk.get_major_version()) + "." + str(Gtk.get_minor_version()) + "." + str(Gtk.get_micro_version()))

    main()
