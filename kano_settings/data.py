#!/usr/bin/env python

# data.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Data functions for getting level specific data from the json

import os
from kano.utils import read_json

filename = os.path.join(os.path.dirname(__file__), 'data/settings.json')
data = read_json(filename)


def get_data(string):
    return data[string]
