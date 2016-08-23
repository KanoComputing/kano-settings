#
# boot_config_filter.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities for the filters found in the boot config file
#

class Filter(object):
    ALL = 'all'
    EDID_TEMPLATE = 'EDID={edid}'

    @classmethod
    def get_edid_filter(cls, edid):
        if not edid:
            return cls.ALL

        return cls.EDID_TEMPLATE.format(edid=edid)
