#
# boot_config_line.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Represents a single line in the boot config file
#

import re

from kano_settings.system.boot_config.boot_config_filter import Filter


class BootConfigLine(object):
    EMPTY = ''
    COMMENT_SYMBOL = '#'
    CONFIG_LINE_PATTERN = r'^\s*(#)?\s*([\w=]+)\s*=\s*(.*)\s*$'
    CONFIG_LINE_RE = re.compile(CONFIG_LINE_PATTERN)

    def __init__(self, line, config_filter=Filter.ALL, debug=False):
        self.line = line
        self.debug = debug

        self.setting, self.value, \
                self.filter, self.is_comment = self.parse_line(line)

        if config_filter != Filter.ALL:
            self.filter = config_filter

    @classmethod
    def parse_line(cls, arg):
        setting = BootConfigLine.EMPTY
        value = BootConfigLine.EMPTY
        config_filter = Filter.ALL
        comment = False

        if isinstance(arg, BootConfigLine):
            setting = arg.setting
            value = arg.value
            config_filter = arg.filter
            comment = arg.is_comment

        elif isinstance(arg, dict):
            setting = arg.get('setting', setting)
            config_filter = arg.get('filter', config_filter)
            value = arg.get('value', value)

        elif isinstance(arg, tuple):
            setting = arg[0]

            if len(arg) >= 2:
                value = arg[1]

            if len(arg) >= 3:
                config_filter = arg[2]

        elif isinstance(arg, basestring):
            match = cls.CONFIG_LINE_RE.match(arg)

            if not match:
                setting = arg.strip(' {}'.format(cls.COMMENT_SYMBOL))
                comment = True
            else:
                groups = match.groups()
                comment = groups[0] == cls.COMMENT_SYMBOL
                setting = groups[1]
                value = groups[2]

        return setting, value, config_filter, comment


    def __eq__(self, other):
        setting, dummy_value, \
            config_filter, dummy_comment = self.parse_line(other)

        return self.setting == setting \
                and self.filter == config_filter
                #TODO and self.value == value \

    def __repr__(self):
        return str(self)

    def __str__(self):
        # Config is incorrectly parsed by RPi if whitespace exists around '='
        value = '={val}'.format(val=self.value) if self.value else ''
        comment = '{} '.format(self.COMMENT_SYMBOL) if self.is_comment else ''
        filter_flag = ' [{}]'.format(self.filter) if \
                self.debug and self.filter != Filter.ALL else ''

        return '{comment}{setting}{val}{filter_flag}'.format(
            comment=comment,
            setting=self.setting,
            val=value,
            filter_flag=filter_flag
        )
