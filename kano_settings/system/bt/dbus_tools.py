# dbus_tools.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Base DBus functions for interacting with the bluetooth devices
#

import dbus

BUS = dbus.SystemBus()

SERVICE_NAME = 'org.bluez'

ROOT_OBJ_PATH = '/'

BASE_DEVICE_OBJ_PATH = '/org/bluez/hci0'
ADAPTER_IFACE_NAME = 'org.bluez.Adapter1'

DEVICE_OBJ_PATH_TEMPLATE = '{base_dev_path}/dev_{{addr}}'.format(
    base_dev_path=BASE_DEVICE_OBJ_PATH
)
DEVICE_IFACE_NAME = 'org.bluez.Device1'

_ROOT_PROXY = None
_ADAPTOR_IFACE = None


def get_root_proxy():
    global _ROOT_PROXY
    if _ROOT_PROXY is None:
        _ROOT_PROXY = BUS.get_object(SERVICE_NAME, ROOT_OBJ_PATH)
    return _ROOT_PROXY


def get_adaptor_iface():
    global _ADAPTOR_IFACE
    if _ADAPTOR_IFACE is None:
        BASE_DEVICE_PROXY = BUS.get_object(SERVICE_NAME, BASE_DEVICE_OBJ_PATH)
        _ADAPTOR_IFACE = dbus.Interface(BASE_DEVICE_PROXY, ADAPTER_IFACE_NAME)
    return _ADAPTOR_IFACE


def get_dbus_object_paths():
    introspect_iface = dbus.Interface(
        get_root_proxy(), 'org.freedesktop.DBus.ObjectManager'
    )
    obj_paths = introspect_iface.GetManagedObjects()

    return [unicode(path) for path in obj_paths.iterkeys()]


def get_device_object_paths():
    obj_paths = get_dbus_object_paths()

    devices = []

    for obj in obj_paths:
        candidate = obj.split(u'{}/'.format(BASE_DEVICE_OBJ_PATH), 1)

        if len(candidate) < 2:
            continue

        if candidate[1]:
            devices.append(obj)

    return devices
