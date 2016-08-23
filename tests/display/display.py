#
# display.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the `kano_settings.system.display` module
#

import contextlib
import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock

import pyfakefs.fake_filesystem as fake_fs


# Import fails if the kano-settings directory doesn't exist
fs = fake_fs.FakeFilesystem()
fs.CreateDirectory('/usr/share/kano-settings')
fake_os = fake_fs.FakeOsModule(fs)
with mock.patch('kano.utils.file_operations.os', fake_os):
    import kano_settings.system.display as display


SETTINGS_FUNCTION_TEMPLATE = 'kano_settings.system.display.{}'
SETTINGS_RUN_CMD = SETTINGS_FUNCTION_TEMPLATE.format('run_cmd')
SETTINGS_SUBPROCESS_CMD = SETTINGS_FUNCTION_TEMPLATE.format(
    'subprocess.check_output'
)
SETTINGS_ISFILE_CMD = SETTINGS_FUNCTION_TEMPLATE.format('os.path.isfile')


def mock_run_cmd(stdout, stderr='', returncode=0):
    def run_cmd(dummy):
        return stdout, stderr, returncode

    return run_cmd


@contextlib.contextmanager
def patched_run_cmd(stdout, stderr='', returncode=0):
    with mock.patch(SETTINGS_RUN_CMD,
                    side_effect=mock_run_cmd(
                        stdout, stderr=stderr, returncode=returncode
                    )):
        yield


@contextlib.contextmanager
def patched_isfile_cmd():
    with mock.patch(SETTINGS_ISFILE_CMD,
                    return_value=True):
        yield


@contextlib.contextmanager
def patched_subprocess_cmd(stdout):
    with mock.patch(SETTINGS_SUBPROCESS_CMD,
                    return_value=stdout):
        yield


class EDIDOperations(unittest.TestCase):
    DISPLAY_NAME_TEMPLATE = 'display_name={}\n'

    VALID_EDID_VAL = 'VSC-TD2220'
    VALID_DISPLAY_NAME = DISPLAY_NAME_TEMPLATE.format(VALID_EDID_VAL)

    EMPTY_EDID_VAL = ''
    EMPTY_DISPLAY_NAME = DISPLAY_NAME_TEMPLATE.format(EMPTY_EDID_VAL)

    def test_get_valid_edid(self):
        with patched_run_cmd(self.VALID_DISPLAY_NAME):
            edid = display.get_edid_name(use_cached=False)

        self.assertEqual(edid, self.VALID_EDID_VAL)

    def test_get_empty_edid(self):
        with patched_run_cmd(self.EMPTY_DISPLAY_NAME):
            edid = display.get_edid_name(use_cached=False)

        self.assertEqual(edid, self.EMPTY_EDID_VAL)

    def test_get_cached_edid(self):
        with patched_run_cmd(self.VALID_DISPLAY_NAME):
            edid = display.get_edid_name(use_cached=True)

        self.assertEqual(edid, self.VALID_EDID_VAL)

        edid = display.get_edid_name(use_cached=True)
        self.assertEqual(edid, self.VALID_EDID_VAL)

    def test_get_failure(self):
        with patched_run_cmd('unused', returncode=1):
            edid = display.get_edid_name(use_cached=False)

        self.assertEqual(edid, None)


TVSERVICE_DMT_OUTPUT = '''Group DMT has 13 modes:
            mode 4: 640x480 @ 60Hz 4:3, clock:25MHz progressive
            mode 5: 640x480 @ 72Hz 4:3, clock:31MHz progressive
            mode 6: 640x480 @ 75Hz 4:3, clock:31MHz progressive
            mode 8: 800x600 @ 56Hz 4:3, clock:36MHz progressive
            mode 9: 800x600 @ 60Hz 4:3, clock:40MHz progressive
            mode 10: 800x600 @ 72Hz 4:3, clock:50MHz progressive
            mode 11: 800x600 @ 75Hz 4:3, clock:49MHz progressive
            mode 16: 1024x768 @ 60Hz 4:3, clock:65MHz progressive
            mode 17: 1024x768 @ 70Hz 4:3, clock:75MHz progressive
            mode 18: 1024x768 @ 75Hz 4:3, clock:78MHz progressive
            mode 39: 1360x768 @ 60Hz 16:9, clock:85MHz progressive
   (prefer) mode 81: 1366x768 @ 60Hz 16:9, clock:85MHz progressive
            mode 85: 1280x720 @ 60Hz 16:9, clock:74MHz progressive
'''


TVSERVICE_CEA_OUTPUT = '''Group CEA has 7 modes:
           mode 1: 640x480 @ 60Hz 4:3, clock:25MHz progressive
           mode 2: 720x480 @ 60Hz 4:3, clock:27MHz progressive
           mode 3: 720x480 @ 60Hz 16:9, clock:27MHz progressive
  (native) mode 4: 1280x720 @ 60Hz 16:9, clock:74MHz progressive
           mode 17: 720x576 @ 50Hz 4:3, clock:27MHz progressive
           mode 18: 720x576 @ 50Hz 16:9, clock:27MHz progressive
           mode 19: 1280x720 @ 50Hz 16:9, clock:74MHz progressive
'''

class SupportedModes(unittest.TestCase):

    def test_dmt_modes(self):
        with patched_isfile_cmd():
            with patched_subprocess_cmd(TVSERVICE_DMT_OUTPUT):
                modes = display.get_supported_modes('DMT')

        expected_val = {
            4: ['640x480', '60Hz', '4:3'],
            5: ['640x480', '72Hz', '4:3'],
            6: ['640x480', '75Hz', '4:3'],
            39: ['1360x768', '60Hz', '16:9'],
            8: ['800x600', '56Hz', '4:3'],
            9: ['800x600', '60Hz', '4:3'],
            10: ['800x600', '72Hz', '4:3'],
            11: ['800x600', '75Hz', '4:3'],
            16: ['1024x768', '60Hz', '4:3'],
            17: ['1024x768', '70Hz', '4:3'],
            18: ['1024x768', '75Hz', '4:3'],
            85: ['1280x720', '60Hz', '16:9'],
            81: ['1366x768', '60Hz', '16:9']
        }
        self.assertEqual(modes, expected_val)

    def test_cea_modes(self):
        with patched_isfile_cmd():
            with patched_subprocess_cmd(TVSERVICE_CEA_OUTPUT):
                modes = display.get_supported_modes('CEA')

        expected_val = {
            1: ['640x480', '60Hz', '4:3'],
            2: ['720x480', '60Hz', '4:3'],
            3: ['720x480', '60Hz', '16:9'],
            4: ['1280x720', '60Hz', '16:9'],
            17: ['720x576', '50Hz', '4:3'],
            18: ['720x576', '50Hz', '16:9'],
            19: ['1280x720', '50Hz', '16:9']
        }
        self.assertEqual(modes, expected_val)
