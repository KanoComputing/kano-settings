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
    MANUAL_COMMENT_PATTERN = r'^\s*###\s*[\w=:][\w=:\s]+\s*$'
    MANUAL_COMMENT_RE = re.compile(MANUAL_COMMENT_PATTERN)

    # This object represents four classes of item:
    
    #  NAME            EXAMPLES             is_comment is_commented_out is_manual_comment
    
    #  Valid setting   "foo=bar","foo=1"    False      False            False
    #  Commented out   "# foo=bar"          True       True             False
    #  Manual Comment  "### foo: bar        True       False            True
    #  Comment         "# NB pi explodes"   True       False            False

    # Valid settings are looked at by the firmware.
    # "Manual Comment" items are data stored in the config.txt not used by the firmware
    # "Commented out" items are example settings which have been commented out.
    # "Comment" items are any other comment


    def __init__(self, line, config_filter=Filter.ALL, debug=False):
        self.line = line
        self.debug = debug

        self.setting, self._value, \
                self.filter, self.is_comment, \
                self.is_manual_comment, self.is_commented_out = self.parse_line(line)

        if config_filter != Filter.ALL:
            self.filter = config_filter

    @classmethod
    def parse_line(cls, arg):
        setting = BootConfigLine.EMPTY
        value = BootConfigLine.EMPTY
        config_filter = Filter.ALL
        comment = False
        manual_comment = False
        commented_out = False

        if isinstance(arg, BootConfigLine):
            setting = arg.setting
            value = arg.value
            config_filter = arg.filter
            comment = arg.is_comment
            commented_out = arg.is_commented_out

        elif isinstance(arg, dict):
            setting = arg.get('setting', setting)
            config_filter = arg.get('filter', config_filter)
            value = arg.get('value', value)
            is_comment = arg.get('is_comment', False)
            commented_out = arg.get('is_commented_out', False)

        elif isinstance(arg, tuple):
            setting = arg[0]

            if len(arg) >= 2:
                value = arg[1]

            if len(arg) >= 3:
                config_filter = arg[2]

        elif isinstance(arg, basestring):
            match = cls.CONFIG_LINE_RE.match(arg)

            if match:
                groups = match.groups()
                comment = groups[0] == cls.COMMENT_SYMBOL
                commented_out = comment
                setting = groups[1]
                value = groups[2]
            else:
                if cls.MANUAL_COMMENT_RE.match(arg):
                    manual_comment = True

                setting = arg.strip(' {}'.format(cls.COMMENT_SYMBOL))
                comment = True

        return setting, value, config_filter, comment, manual_comment, commented_out


    def __eq__(self, other):
        setting, dummy_value, \
            config_filter, dummy_comment, \
            dummy_manual_comment, dummy_commented_out = self.parse_line(other)

        return self.setting == setting \
                and self.filter == config_filter
                # TODO and self.value == value \

    def __repr__(self):
        return str(self)

    def __str__(self):
        if not self.setting:
            return ''

        # Normally we want settings to have an '=' and value but this object can represent a pure
        # comment, in which case there is no value so we want an empty string for the 'value'
        if self.is_comment and not self.is_commented_out:
            default_value_str = ''
        else:
            default_value_str = '=0'

        # Config is incorrectly parsed by RPi if whitespace exists around '='
        value = '={val}'.format(val=self._value) if self._value else default_value_str

        if self.is_comment:
            comment_symbol_multiplier = 3 if self.is_manual_comment else 1
            comment = '{} '.format(
                comment_symbol_multiplier * self.COMMENT_SYMBOL
            )
        else:
            comment = ''

        filter_flag = ' [{}]'.format(self.filter) if \
                self.debug and self.filter != Filter.ALL else ''

        return '{comment}{setting}{val}{filter_flag}'.format(
            comment=comment,
            setting=self.setting,
            val=value,
            filter_flag=filter_flag
        )

    @property
    def value(self):
        if not self._value:
            return 0

        try:
            return int(self._value)
        except ValueError:
            return self._value

    @value.setter
    def value(self, val):
        self._value = str(val)
