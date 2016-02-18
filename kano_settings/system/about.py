#!/usr/bin/env python

# about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the about screen backend functions


from kano.utils import run_cmd, get_rpi_model


def get_current_version():
    version_number = "?"
    with open('/etc/kanux_version', 'r') as f:
        output = f.read().strip()
        version_number = output.split('-')[-1]
    return version_number


def get_space_available():
    out, err, rc = run_cmd('df -h / | tail -1')
    device, size, used, free, percent, mp = out.split()

    info = {
        'used': '',
        'total': ''
    }

    if not err:
        info['used'] = used
        info['total'] = size

    return info


def get_temperature():
    temperature = None
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        output = f.read().strip()
        temperature = int(output) / 1000.0
    return temperature


def get_model_name():
    model_name = get_rpi_model()
    # TODO: Good enough for now but re should review this
    model = model_name.split('RPI/', 1)[-1].split('/', 1)[0]

    return "Raspberry Pi {}".format(model)
