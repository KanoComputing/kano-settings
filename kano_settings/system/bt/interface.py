# interface.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Bluetooth manipulation functions
#

import dbus
import threading

from kano.logging import logger

from kano_settings.system.bt.dbus_tools import BUS, SERVICE_NAME, \
    DEVICE_OBJ_PATH_TEMPLATE, DEVICE_IFACE_NAME, get_adaptor_iface, \
    BASE_DEVICE_OBJ_PATH, get_dbus_object_paths, get_device_object_paths
from kano_settings.system.bt.device import BluetoothDevice


def is_bluetooth_available():
    try:
        dbus_obj_paths = get_dbus_object_paths()

        return BASE_DEVICE_OBJ_PATH in dbus_obj_paths
    except Exception as e:
        logger.error("Couldn't connect to DBus to see if bluetooth is " \
                     "available, asuming not",
                     exception=e)
        return False


def get_available_devices(discard_unsupported=True):
    dev_paths = get_device_object_paths()
    devices = [
        BluetoothDevice(dev) for dev in dev_paths
    ]

    return [
        dev for dev in devices if not discard_unsupported or dev.is_supported()
    ]


def get_device_interface(device_addr, async=False):
    dbus_proxy = BUS.get_object(
        SERVICE_NAME,
        DEVICE_OBJ_PATH_TEMPLATE.format(device_addr.replace(':', '_')),
        follow_name_owner_changes=async
    )
    interface = dbus.Interface(dbus_proxy, DEVICE_IFACE_NAME)

    return interface


def clear_all_devices(retain_connected=True, retain_trusted=True):
    devices = get_available_devices()
    for device in devices:
        if retain_connected and device.connected:
            continue

        if retain_trusted and device.trusted:
            continue

        get_adaptor_iface().RemoveDevice(device.dbus_dev_obj_path)


def discover_devices():
    if not is_bluetooth_available():
        logger.warn("No bluetooth available")
        return

    try:
        get_adaptor_iface().StartDiscovery()
    except dbus.DBusException as e:
        logger.error("Error entering bluetooth discovery mode. " \
                     "This is likely because DBus isn't ready",
                     exception=e)


def stop_discovering_devices():
    if not is_bluetooth_available():
        logger.warn("No bluetooth available")
        return

    try:
        get_adaptor_iface().StopDiscovery()
    except dbus.DBusException as e:
        logger.error("Error exiting bluetooth discovery mode. " \
                     "This is likely because DBus isn't ready",
                     exception=e)


def device_scan(callback, clear=True, timeout=10, *cb_args, **cb_kwargs):
    if not is_bluetooth_available():
        logger.warn("No bluetooth available")
        return

    if clear:
        clear_all_devices()

    def parse_results(callback):
        stop_discovering_devices()
        devices = get_available_devices()
        callback(devices, *cb_args, **cb_kwargs)

    scan_thr = threading.Timer(
        timeout, parse_results, kwargs={'callback': callback}
    )

    discover_devices()
    scan_thr.start()
