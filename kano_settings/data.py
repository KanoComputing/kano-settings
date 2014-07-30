#!/usr/bin/env python

# data.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Data functions for getting level specific data from the json

import json
import os


def get_data(string):

    filename = os.path.join("/usr/lib/python2.7/dist-packages/kano_settings/data/settings.json")
    json_data = open(filename)
    data = json.load(json_data)
    stage_data = data[string]
    return stage_data
