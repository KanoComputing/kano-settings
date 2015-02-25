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
    output = subprocess.check_output(["cat", "/etc/kanux_version"])
    version_number = output.split("-")[-1].strip()
    return "Kano OS v." + version_number


def get_space_available():
    output = subprocess.check_output("df -h | grep rootfs", shell=True)
    items = output.strip().split(" ")
    items = filter(None, items)
    total_space = items[1]
    space_used = items[2]
    return "Disk space used: " + space_used + "B / " + total_space + "B"


def get_temperature():
    degree_sign = u'\N{DEGREE SIGN}'
    output = subprocess.check_output("cputemp0=`cat /sys/class/thermal/thermal_zone0/temp`; \
                                     cputemp1=$(($cputemp0/1000)); \
                                     cputemp2=$(($cputemp0/100)); \
                                     cputemp=$(($cputemp2%$cputemp1)); \
                                     echo $cputemp1\".\"$cputemp", shell=True)
    output = output.strip()
    return "Temperature: " + output + degree_sign + "C"


def get_model_name():
    board_info = "Model: Raspberry Pi"
    if is_model_a():
        board_info += " A"
    elif is_model_b():
        board_info += " B"
    elif is_model_b_plus():
        board_info += " B+"
    elif is_model_2_b():
        board_info += " 2"

    return board_info
