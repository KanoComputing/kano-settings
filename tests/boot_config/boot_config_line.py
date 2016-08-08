#
# boot_config_line.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the `kano_settings.system.boot_config.boot_config_line` module
#

import unittest
import warnings

from kano_settings.system.boot_config.boot_config_filter import Filter
from kano_settings.system.boot_config.boot_config_parser import BootConfigLine


class ConfigLineTest(unittest.TestCase):

    def validate_line(self, config_line, setting, value,
                      config_filter=Filter.ALL, is_comment=False):
        self.assertEqual(config_line.setting, setting)
        self.assertEqual(config_line.value, value)
        self.assertEqual(config_line.filter, config_filter)
        self.assertEqual(config_line.is_comment, is_comment)


class ParsingConfigLineStringTest(ConfigLineTest):
    def test_simple_line(self):
        key = 'hdmi_safe'
        val = 1
        line = BootConfigLine('{}={}'.format(key, val))
        self.validate_line(line, key, str(val))

    def test_comment_line(self):
        key = 'hdmi_safe'
        val = 1
        line = BootConfigLine('# {}={}'.format(key, val))
        self.validate_line(line, key, str(val), is_comment=True)

    def test_compound_line(self):
        key = 'dtparam=i2c_arm'
        val = 'on'
        line = BootConfigLine('{}={}'.format(key, val))
        self.validate_line(line, key, val)

    def test_filter_line(self):
        key = 'hdmi_safe'
        val = 1
        config_filter = 'rpi3'
        line = BootConfigLine(
            '{}={}'.format(key, val), config_filter=config_filter
        )
        self.validate_line(line, key, str(val), config_filter=config_filter)


class ParsingConfigLineTupleTest(ConfigLineTest):
    def setUp(self):
        self.base_line = BootConfigLine('dtparam=i2c_arm=on')

    def test_single_tuple(self):
        line = BootConfigLine((self.base_line.setting,))
        self.validate_line(line, self.base_line.setting, '')

    def test_double_tuple(self):
        line = BootConfigLine((
            self.base_line.setting,
            self.base_line.value
        ))
        self.validate_line(line, self.base_line.setting, self.base_line.value)

    def test_triple_tuple(self):
        line = BootConfigLine((
            self.base_line.setting,
            self.base_line.value,
            self.base_line.filter
        ))
        self.validate_line(line, self.base_line.setting, self.base_line.value,
                           self.base_line.filter)


class ParsingConfigLineDictTest(ConfigLineTest):
    def setUp(self):
        self.base_line = BootConfigLine('dtparam=i2c_arm=on')

    def test_setting_dict(self):
        line = BootConfigLine({
            'setting': self.base_line.setting,
        })
        self.validate_line(line, self.base_line.setting, '')

    def test_setting_value_dict(self):
        line = BootConfigLine({
            'setting': self.base_line.setting,
            'value': self.base_line.value,
        })
        self.validate_line(line, self.base_line.setting, self.base_line.value)

    def test_setting_value_filter_dict(self):
        line = BootConfigLine({
            'setting': self.base_line.setting,
            'value': self.base_line.value,
            'filter': self.base_line.filter,
        })
        self.validate_line(line, self.base_line.setting, self.base_line.value,
                           config_filter=self.base_line.filter)

    def test_setting_value_filter_comment_dict(self):
        line = BootConfigLine({
            'setting': self.base_line.setting,
            'value': self.base_line.value,
            'filter': self.base_line.filter,
            'is_comment': self.base_line.is_comment
        })
        self.validate_line(
            line,
            self.base_line.setting,
            self.base_line.value,
            config_filter=self.base_line.filter,
            is_comment=self.base_line.is_comment
        )

class ParsingConfigLineCopyTest(ConfigLineTest):
    def setUp(self):
        self.base_line = BootConfigLine('dtparam=i2c_arm=on')
        self.copy_line = BootConfigLine(self.base_line)

    def test_copy(self):
        self.validate_line(
            self.copy_line,
            self.base_line.setting,
            self.base_line.value,
            config_filter=self.base_line.filter,
            is_comment=self.base_line.is_comment
        )

    def test_equality(self):
        self.assertEqual(self.base_line, self.copy_line)

        line = BootConfigLine(self.base_line)
        line.is_comment = True
        self.assertNotEqual(self.base_line, line)

        line = BootConfigLine(self.base_line)
        line.config_filter = 'rpi3'
        self.assertNotEqual(self.base_line, line)

        line = BootConfigLine(self.base_line)
        line.value = 'off'
        self.assertNotEqual(self.base_line, line)
        self.assertEqual(self.base_line, line)
        warnings.warn('This test doesn\'t seem to work')

        line = BootConfigLine(self.base_line)
        line.setting = 'hdmi_mode'
        self.assertNotEqual(self.base_line, line)
