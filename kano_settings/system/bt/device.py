# device.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Interface to a bluetooth device
#

import dbus

from kano.logging import logger
from kano.utils.dbus_interface import get_property, get_all_properties, \
    set_property, dbus_to_bool
from kano.decorators import retry

from kano_settings.system.bt.dbus_tools import BUS, SERVICE_NAME, \
    DEVICE_IFACE_NAME


class BluetoothDevice(object):

    def __init__(self, dbus_dev_obj_path):
        super(BluetoothDevice, self).__init__()

        self.dbus_dev_obj_path = dbus_dev_obj_path
        self._dbus_proxy = self.get_dbus_proxy()
        self.interface = self.get_device_interface()

        props = self.get_properties()
        logger.debug(u"Properties: {}".format(props))

        self._name = props.get('Name', '')
        self._alias = props.get('Alias', '')
        self._addr = props.get('Address', '')
        self.icon = props.get('Icon', '')
        self.class_id = props.get('Class', '')

    def __unicode__(self):
        return u'{} ({})'.format(self.name, self.addr)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def is_supported(self):
        return bool(self.class_id)

    def get_dbus_proxy(self, async=False):
        dbus_proxy = BUS.get_object(
            SERVICE_NAME,
            self.dbus_dev_obj_path,
            follow_name_owner_changes=async
        )
        return dbus_proxy

    def get_device_interface(self):
        interface = dbus.Interface(self._dbus_proxy, DEVICE_IFACE_NAME)

        return interface

    def get_properties(self):
        return get_all_properties(self._dbus_proxy, DEVICE_IFACE_NAME)

    def get_property(self, prop):
        return get_property(self._dbus_proxy, DEVICE_IFACE_NAME, prop)

    def set_property(self, prop, val):
        return set_property(self._dbus_proxy, DEVICE_IFACE_NAME, prop, val)

    @property
    def name(self):
        return self._name or self._alias

    @property
    def alias(self):
        return self._alias

    @property
    def addr(self):
        return self._addr

    @property
    def connected(self):
        return dbus_to_bool(self.get_property('Connected'))

    @property
    def paired(self):
        return dbus_to_bool(self.get_property('Paired'))

    @retry(3, delay=1, backoff=2)
    def pair(self):
        if self.paired:
            return

        self.interface.Pair()
        return self.paired

    @retry(3, delay=1, backoff=2)
    def connect(self):
        if self.connected:
            return

        try:
            self.interface.Connect()
        except dbus.DBusException:
            # Probably means the device has come out of discover mode
            return False
        return self.connected

    def disconnect(self):
        if not self.connected:
            return

        self.interface.Disconnect()
        return not self.connected

    def fuse(self):
        '''
        Perform actions to bind this device to the adapter
        '''
        try:
            self.pair()
            self.connect()
            self.trusted = self.paired
            return self.trusted
        except dbus.DBusException:
            logger.error(
                "Fusing failed: the dbus service probably did not reply"
            )
            return False

    def unfuse(self):
        try:
            self.trusted = False
            self.disconnect()
            return True
        except dbus.DBusException:
            logger.error(
                "Unfusing failed: the dbus service probably did not reply"
            )
            return False

    @property
    def trusted(self):
        return dbus_to_bool(self.get_property('Trusted'))

    @trusted.setter
    def trusted(self, val):
        if not isinstance(val, bool):
            return

        self.set_property('Trusted', val)

    def set_trusted(self):
        self.trusted = True

    def set_untrusted(self):
        self.trusted = False
