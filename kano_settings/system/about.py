#!/usr/bin/env python

# about.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the about screen backend functions

import subprocess
from kano.utils import is_model_a, is_model_b, is_model_b_plus, is_model_2_b


def get_current_version():
    version_number = "?"
    with open('/etc/kanux_version', 'r') as f:
        output = f.read().strip()
        version_number = output.split('-')[-1]
    return version_number


def get_space_available():
    output = subprocess.check_output("df -h | grep rootfs", shell=True)
    items = output.strip().split(' ')
    items = filter(None, items)
    return {
        'used': items[1],
        'total': items[2]
    }


def get_temperature():
    temperature = None
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        output = f.read().strip()
        temperature = int(output) / 1000.0
    return temperature


def get_model_name():
    if is_model_a():
        model = "A"
    elif is_model_b():
        model = "B"
    elif is_model_b_plus():
        model = "B+"
    elif is_model_2_b():
        model = "2"

    return "Raspberry Pi {}".format(model)
