# boot_config_filter.py
#
# Copyright (C) 2016-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities for the filters found in the boot config file
# https://www.raspberrypi.org/documentation/configuration/config-txt/conditional.md


class Filter(object):

    ALL = 'all'
    EDID_TEMPLATE = 'EDID={edid}'
    PI0 = 'pi0'
    PI1 = 'pi1'
    PI2 = 'pi2'
    PI3 = 'pi3'
    NONE = 'none'

    @classmethod
    def get_edid_filter(cls, edid):
        if not edid:
            return cls.ALL

        return cls.EDID_TEMPLATE.format(edid=edid)

    @classmethod
    def get_pi0_filter(cls):
        return cls.PI0

    @classmethod
    def get_pi1_filter(cls):
        return cls.PI1

    @classmethod
    def get_pi2_filter(cls):
        return cls.PI2

    @classmethod
    def get_pi3_filter(cls):
        return cls.PI3

    @classmethod
    def get_none_filter(cls):
        return cls.NONE
