#
# test_locale.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This module tests the detection of all RaspberryPI models
#


import unittest
import sys
import os

sys.path.insert(1, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import kano_settings.system.locale as locale
import kano.utils as utils

from tests.tools import test_print, mock_file


print '''
***************************
******* Test Locale *******
***************************

To for the tests to be fair, ensure that you have installed:
    en_US.UTF-8
    en_GB.UTF-8
And that you have removed:
    ru_RU.UTF-8
    aa_ER.UTF-8
'''


class EnsureUTFLocale(unittest.TestCase):

    def test_with_utf_suffix(self):
        self.assertEqual(locale.ensure_utf_locale('en_GB.UTF-8'), 'en_GB.UTF-8')

    def test_without_utf_suffix(self):
        self.assertEqual(locale.ensure_utf_locale('en_GB'), 'en_GB.UTF-8')

    def test_with_wrong_suffix(self):
        self.assertEqual(locale.ensure_utf_locale('en_GB.ISO-8859-1'),
                         'en_GB.UTF-8')


class StripEncodingFromLocale(unittest.TestCase):

    def test_with_utf_suffix(self):
        self.assertEqual(
            locale.strip_encoding_from_locale('en_GB.UTF-8'), 'en_GB'
        )

    def test_without_utf_suffix(self):
        self.assertEqual(locale.strip_encoding_from_locale('en_GB'), 'en_GB')

    def test_with_wrong_suffix(self):
        self.assertEqual(
            locale.strip_encoding_from_locale('en_GB.ISO-8859-1'), 'en_GB'
        )


class StandardLocaleToGenfileEntry(unittest.TestCase):

    def test(self):
        test_locale = locale.ensure_utf_locale('en_GB')

        self.assertEqual(locale.standard_locale_to_genfile_entry(test_locale),
                         r'en_GB[\.\s]UTF-8(\sUTF-8)?')



class IsLocaleValid(unittest.TestCase):

    def test_is_en_US_valid(self):
        self.assertTrue(locale.is_locale_valid('en_US.UTF-8'))

    def test_is_en_GB_valid(self):
        self.assertTrue(locale.is_locale_valid('en_GB.UTF-8'))

    def test_is_random_string_valid(self):
        self.assertFalse(locale.is_locale_valid('some_invalid_locale'))


class IsLocaleInstalled(unittest.TestCase):

    def test_is_en_US_installed(self):
        self.assertTrue(locale.is_locale_installed('en_US.UTF-8'))

    def test_is_en_GB_installed(self):
        self.assertTrue(locale.is_locale_installed('en_GB.UTF-8'))

    def test_is_ru_RU_installed(self):
        self.assertFalse(locale.is_locale_installed('ru_RU.UTF-8'))

    def test_is_aa_ER_installed(self):
        self.assertFalse(locale.is_locale_installed('aa_ER.UTF-8'))

    def test_is_random_string_installed(self):
        self.assertFalse(locale.is_locale_installed('some_ininstalled_locale'))


class InstallLocale(unittest.TestCase):

    def test_install_locale(self):
        test_locale = 'aa_ER'
        locale_already_installed = locale.is_locale_installed(test_locale)

        if locale_already_installed:
            test_print('Locale already installed so uninstalling...')
            locale.uninstall_locale(test_locale)

            if locale.is_locale_installed(test_locale):
                test_print('ERROR: Locale could not be removed')
                return

        locale.install_locale(test_locale)

        self.assertTrue(locale.is_locale_installed(test_locale))

        # Revert the state
        if not locale_already_installed:
            test_print('Restoring original locale state')
            locale.uninstall_locale(test_locale)


class UninstallLocale(unittest.TestCase):

    def test_uninstall_locale(self):
        test_locale = 'aa_ER'
        locale_already_installed = locale.is_locale_installed(test_locale)

        if not locale_already_installed:
            test_print('Locale not installed so installing...')
            locale.install_locale(test_locale)

            if not locale.is_locale_installed(test_locale):
                test_print('ERROR: Locale could not be installed')
                return

        locale.uninstall_locale(test_locale)

        self.assertFalse(locale.is_locale_installed(test_locale))

        # Revert the state
        if locale_already_installed:
            test_print('Restoring original locale state')
            locale.install_locale(test_locale)


class SetLocaleParam(unittest.TestCase):

    def run_test_for_param(self, param):
        with mock_file(locale.XSESSION_RC_FILE):
            test_locale = 'en_US.UTF-8'
            config_line = 'export {}={}'.format(param, test_locale)
            locale.set_locale_param(param, test_locale)

            config = utils.read_file_contents_as_lines(locale.XSESSION_RC_FILE)

            self.assertTrue(config_line in config)

    def test_xsession_rc_file_path(self):
        self.assertEqual(locale.XSESSION_RC_FILE,
                         os.path.join('/home', utils.get_user_unsudoed(),
                                      '.xsessionrc'))

    def test_LANGUAGE_set(self):
        self.run_test_for_param('LANGUAGE')

    def test_LC_ADDRESS_set(self):
        self.run_test_for_param('LC_ADDRESS')

    def test_LC_COLLATE_set(self):
        self.run_test_for_param('LC_COLLATE')

    def test_LC_CTYPE_set(self):
        self.run_test_for_param('LC_CTYPE')

    def test_LC_MONETARY_set(self):
        self.run_test_for_param('LC_MONETARY')

    def test_LC_MEASUREMENT_set(self):
        self.run_test_for_param('LC_MEASUREMENT')

    def test_LC_MESSAGES_set(self):
        self.run_test_for_param('LC_MESSAGES')

    def test_LC_NUMERIC_set(self):
        self.run_test_for_param('LC_NUMERIC')

    def test_LC_PAPER_set(self):
        self.run_test_for_param('LC_PAPER')

    def test_LC_RESPONSE_set(self):
        self.run_test_for_param('LC_RESPONSE')

    def test_LC_TELEPHONE_set(self):
        self.run_test_for_param('LC_TELEPHONE')

    def test_LC_TIME_set(self):
        self.run_test_for_param('LC_TIME')


class SetLocale(unittest.TestCase):

    def test_set_locale(self):
        with mock_file(locale.XSESSION_RC_FILE):
            params = [
                'LANGUAGE',
                'LC_ADDRESS',
                'LC_COLLATE',
                'LC_CTYPE',
                'LC_MONETARY',
                'LC_MEASUREMENT',
                'LC_MESSAGES',
                'LC_NUMERIC',
                'LC_PAPER',
                'LC_RESPONSE',
                'LC_TELEPHONE',
                'LC_TIME'
            ]

            test_locale = 'en_US.UTF-8'
            config_lines = [
                'export {}={}'.format(param, test_locale) for param in params
            ]
            locale.set_locale(test_locale)

            config = utils.read_file_contents_as_lines(locale.XSESSION_RC_FILE)
            for line in config_lines:
                if line not in config:
                    self.assertFalse(True)

            self.assertTrue(True)
