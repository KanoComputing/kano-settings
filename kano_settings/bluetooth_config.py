# bluetooth_config.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Bluetooth setup screen
#

import os
import threading
from gi.repository import Gtk, GObject

from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.buttons import KanoButton
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.blur_overlay import BlurOverlay
from kano.logging import logger
from kano.decorators import queue_cb

from kano_settings.common import IMAGES_DIR
from kano_settings.templates import Template
from kano_settings.system.bt.interface import is_bluetooth_available, \
    device_scan


class BluetoothDeviceItem(Gtk.Box):
    __gsignals__ = {
        'pairing': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'done-pairing': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, device):
        Gtk.Box.__init__(self, hexpand=True)

        self.device = device
        device_name = device.name

        dev_label = Gtk.Label(device_name, hexpand=True)
        dev_label.get_style_context().add_class('normal_label')
        self.pack_start(dev_label, False, False, 0)

        self._pair_button = KanoButton()
        self._set_paired_button_state()
        self._pair_button.set_margin_top(10)
        self._pair_button.set_margin_bottom(10)
        self._pair_button.set_margin_left(10)
        self._pair_button.set_margin_right(10)
        self._pair_button.connect('clicked', self.pair)
        self.pack_start(self._pair_button, False, False, 0)

    def _set_paired_button_state(self, *dummy_args, **dummy_kwargs):
        if not self.device.connected:
            label = 'Pair'.upper()
            colour = 'green'
        else:
            label = 'Unpair'.upper()
            colour = 'red'

        self._pair_button.set_label(label)
        self._pair_button.set_color(colour)

    def error(self, err_msg):
        KanoDialog(err_msg).run()

    def pair(self, *dummy_args, **dummy_kwargs):
        def done_pairing():
            self._set_paired_button_state()
            self.emit('done-pairing')

        @queue_cb(callback=done_pairing, gtk=True)
        def do_pair():
            if not self.device.fuse():
                GObject.idle_add(self.error, 'Pairing failed')

        @queue_cb(callback=done_pairing, gtk=True)
        def do_unpair():
            if not self.device.unfuse():
                GObject.idle_add(self.error, 'Unpairing failed')

        self.emit('pairing')

        if self.device.connected:
            pair_fn = do_unpair
            logger.info(u'Unpairing {}'.format(self.device).encode('utf-8'))
        else:
            pair_fn = do_pair
            logger.info(u'Pairing {}'.format(self.device).encode('utf-8'))

        pair_thr = threading.Thread(target=pair_fn)
        pair_thr.start()


class BluetoothDevicesList(ScrolledWindow):
    __gsignals__ = {
        'loading': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'done-loading': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self):
        ScrolledWindow.__init__(self, hexpand=True, vexpand=True)
        self.set_size_request(500, 300)

        self.contents = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add_with_viewport(self.contents)

        self.devices = []
        self.dev_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.contents.pack_start(self.dev_view, False, False, 0)

    def add_device(self, device, idx=0):
        dev_item = BluetoothDeviceItem(device)
        dev_item.connect('pairing', self.set_loading)
        dev_item.connect('done-pairing', self.unset_loading)

        css_class = 'white-bg' if idx % 2 else 'grey-bg'
        dev_item.get_style_context().add_class(css_class)

        self.dev_view.pack_start(dev_item, False, False, 0)

        self.dev_view.show_all()

    def empty(self):
        for device in self.dev_view.get_children():
            self.dev_view.remove(device)

    def set_no_adapter_available(self):
        no_adapter = Gtk.Label('No bluetooth dongle detected')
        no_adapter.get_style_context().add_class('normal_label')
        self.dev_view.pack_start(no_adapter, False, False, 0)

        self.dev_view.show_all()

    def set_no_devices_nearby(self):
        no_dev = Gtk.Label('No devices found nearby')
        no_dev.get_style_context().add_class('normal_label')
        self.dev_view.pack_start(no_dev, False, False, 0)

        self.dev_view.show_all()

    def set_loading(self, *dummy_args, **dummy_kwargs):
        logger.debug('loading...')
        self.emit('loading')

    def unset_loading(self, *dummy_args, **dummy_kwargs):
        logger.debug('done loading')
        self.emit('done-loading')

    def populate(self):
        def _end_populate():
            self.unset_loading()

        @queue_cb(callback=_end_populate, gtk=True)
        def _do_populate(devices):
            if not devices:
                logger.info('No devices')
                GObject.idle_add(self.set_no_devices_nearby)

            for idx, device in enumerate(devices):
                logger.info(u'Adding device {}'.format(device).encode('utf-8'))
                GObject.idle_add(self.add_device, device, idx)

        if not is_bluetooth_available():
            logger.info('No adapter')
            self.set_no_adapter_available()
            return

        self.set_loading()
        device_scan(_do_populate)


    def refresh(self, *dummy_args, **dummy_kwargs):
        self.empty()
        self.populate()


class BluetoothConfig(Template):

    def __init__(self, win):
        Template.__init__(
            self,
            "Bluetooth",
            "Connect to bluetooth devices",
            "APPLY CHANGES",
            win.is_plug(),
            back_btn=True
        )

        self.win = win
        self.win.set_main_widget(self)
        self.win.top_bar.enable_prev()
        self.win.change_prev_callback(self.win.go_to_home)

        self._overlay = BlurOverlay()
        self.box.pack_start(self._overlay, False, False, 0)

        self._contents = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.fill_contents()
        self._overlay.add(self._contents)

        self._refresh_btn = None
        self._done_btn = None
        self._arrange_buttons()

        self.show_all()

        self.dev_list.refresh()

    def _arrange_buttons(self):
        self.remove(self.kano_button.align)

        btn_box = Gtk.Box()
        btn_box.set_valign(Gtk.Align.CENTER)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(30)
        btn_box.set_margin_bottom(30)

        self._refresh_btn = refresh_button = KanoButton(color='orange')
        refresh_icon_filepath = os.path.join(IMAGES_DIR, 'refresh.png')
        refresh_icon = Gtk.Image.new_from_file(refresh_icon_filepath)
        refresh_button.set_image(refresh_icon)
        refresh_button.set_margin_right(10)
        refresh_button.connect('clicked', self.dev_list.refresh)
        btn_box.pack_start(refresh_button, False, False, 0)

        self._done_button = done_btn = KanoButton('Done'.upper())
        done_btn.connect('clicked', self.win.go_to_home)
        btn_box.pack_start(done_btn, False, False, 0)

        self.pack_end(btn_box, False, False, 0)

    def fill_contents(self):
        self.dev_list = BluetoothDevicesList()
        self.dev_list.connect('loading', self.blur)
        self.dev_list.connect('done-loading', self.unblur)
        self._contents.pack_start(self.dev_list, False, False, 0)

    def blur(self, *dummy_args, **dummy_kwargs):
        self._overlay.blur()
        self._refresh_btn.set_sensitive(False)
        self._done_button.set_sensitive(False)
        self.win.top_bar.disable_prev()

    def unblur(self, *dummy_args, **dummy_kwargs):
        self._overlay.unblur()
        self._refresh_btn.set_sensitive(True)
        self._done_button.set_sensitive(True)
        self.win.top_bar.enable_prev()
