import re
import unittest
import warnings

from kano_settings.boot_config_parser import BootConfigParser

BASE_TEST_CONFIG = '''
# uncomment if you get no picture on HDMI for a default "safe" mode
#hdmi_safe=1

# Force sound to go through the analog output even if an HDMI monitor is plugged in
# Not strictly necessary for most apps that default to local device (sonic-pi).
hdmi_ignore_edid_audio=1

# 1 -> perfect size
# 0 -> added black border for TVs
disable_overscan=1

# Use the following to adjust overscan. Use positive numbers if console
# goes off screen, and negative if there is too much border
# the zero setting for CEA is -48, for DMT is 0
overscan_left=0
overscan_right=0
overscan_top=0
overscan_bottom=0

# Force RGB full range (0-255)
hdmi_pixel_encoding=2

# Force Kanux display size.
#framebuffer_width=1024
#framebuffer_height=768

# uncomment if hdmi display is not detected and composite is being output
hdmi_force_hotplug=1

# uncomment to force a specific HDMI mode (this will force VGA)
#hdmi_group=1
#hdmi_mode=1

# uncomment to force a HDMI mode rather than DVI. This can make audio work in
# DMT (computer monitor) modes
#hdmi_drive=2

# uncomment to increase signal to HDMI, if you have interference, blanking, or
# no display
#config_hdmi_boost=4

# uncomment for composite PAL
#sdtv_mode=2

# Enabling Turbo Mode
# Please, beware "force_turbo=1" will set the sticky bit
# on your RPi unit forever.
#
force_turbo=0
arm_freq=900
core_freq=250
sdram_freq=450
over_voltage=0

# set memory split: amount allocated to the GPU in MB.
gpu_mem=128

# Toggles PiCamera on(1) and off(0)
start_x=0

# Set max_usb_current flag to 1 if you need to drive usb devices > 500ma current
# Note: RaspberryPI model B+ only
max_usb_current=0

# Enable I2C to allow speaker LEDs to work.
dtparam=i2c_arm=on
dtparam=i2c1=on

# for more options see http://elinux.org/RPi_config.txt
[EDID=VSC-TD2220]
hdmi_group=2
hdmi_mode=82
[rpi3]
arm_freq=1200
[all]
hdmi_group=1
'''


class BootConfigParserTest(unittest.TestCase):
    SANITISE_EMPTY_PATTERN = r'^[\s#]*$'
    SANITISE_EMPTY_RE = re.compile(SANITISE_EMPTY_PATTERN, re.MULTILINE)

    SANITISE_COMMENTS_PATTERN = r'^\s*#\s*(.*)$'
    SANITISE_COMMENTS_RE = re.compile(SANITISE_COMMENTS_PATTERN, re.MULTILINE)

    SANITISE_SPACING_PATTERN = r'\s*=\s*'
    SANITISE_SPACING_RE = re.compile(SANITISE_SPACING_PATTERN, re.MULTILINE)

    def setUp(self):
        self.base_config = BASE_TEST_CONFIG
        self.config = BootConfigParser(self.base_config)

    def tearDown(self):
        pass

    def sanitise_config(self, config):
        new_config = self.SANITISE_EMPTY_RE.sub('', config)
        new_config = self.SANITISE_COMMENTS_RE.sub('# \1', config)
        new_config = self.SANITISE_SPACING_RE.sub(' = ', new_config)

        return new_config.splitlines()


class CheckParsingConfig(BootConfigParserTest):

    def compare_config_dumps(self, config_1, config_2):
        self.assertEqual(
            self.sanitise_config(config_1),
            self.sanitise_config(config_2)
        )

    def test_dump_same(self):
        dump = self.config.dump()
        self.compare_config_dumps(self.base_config, dump)

    def test_list_init(self):
        test = BootConfigParser(self.base_config.splitlines())
        self.compare_config_dumps(self.base_config, test.dump())

    def check_null_get(self, null_conf):
        key = 'hdmi_mode'
        line = null_conf.get(key)

        self.assertEqual(line.setting, key)
        self.assertEqual(line.value, '')

    def test_none_init(self):
        test = BootConfigParser(None)
        self.check_null_get(test)

    def test_empty_string_init(self):
        test = BootConfigParser('')
        self.check_null_get(test)

    def test_empty_list_init(self):
        test = BootConfigParser([])
        self.check_null_get(test)

    def test_iter(self):
        self.assertEqual(len(self.config), len([_ for _ in self.config]))


class CheckGettingConfigValues(BootConfigParserTest):

    def test_getting_unique_value(self):
        sdram_freq = self.config.get('sdram_freq')
        self.assertEqual(sdram_freq.value, '450')
        self.assertEqual(sdram_freq.is_comment, False)

    def test_getting_duplicate_value(self):
        arm_freq = self.config.get('arm_freq')
        self.assertEqual(arm_freq.value, '900')
        self.assertEqual(arm_freq.is_comment, False)

        arm_freq_rpi3 = self.config.get('arm_freq', 'rpi3')
        self.assertEqual(arm_freq_rpi3.value, '1200')
        self.assertEqual(arm_freq_rpi3.is_comment, False)

    def test_getting_commented_value(self):
        sdtv_mode = self.config.get('sdtv_mode')
        self.assertEqual(sdtv_mode.value, '2')
        self.assertEqual(sdtv_mode.is_comment, True)

    def test_getting_compound_key(self):
        dtparam_mode = self.config.get('dtparam=i2c_arm')
        self.assertEqual(dtparam_mode.value, 'on')
        self.assertEqual(dtparam_mode.is_comment, False)

    def test_get_reset_value(self):
        hdmi_group = self.config.get('hdmi_group')
        self.assertEqual(hdmi_group.value, '1')
        self.assertEqual(hdmi_group.is_comment, False)

        warnings.warn(
            'Should the value returned from `get` be the old value '
            'or the new one?'
        )
        hdmi_group_rpi3 = self.config.get('hdmi_group', 'EDID=VSC-TD2220')
        self.assertEqual(hdmi_group_rpi3.value, '2')
        self.assertEqual(hdmi_group_rpi3.is_comment, False)


class CheckSettingConfigValues(BootConfigParserTest):

    def test_setting_unique_value(self):
        new_val = 400
        self.config.set('sdram_freq', new_val)

        sdram_freq = self.config.get('sdram_freq')
        self.assertEqual(sdram_freq.value, new_val)
        self.assertEqual(sdram_freq.is_comment, False)

    def test_setting_duplicate_value(self):
        new_val = 400
        new_rpi3_val = 800
        self.config.set('arm_freq', new_val)
        self.config.set('arm_freq', new_rpi3_val, 'rpi3')

        arm_freq = self.config.get('arm_freq')
        self.assertEqual(arm_freq.value, new_val)
        self.assertEqual(arm_freq.is_comment, False)

        arm_freq_rpi3 = self.config.get('arm_freq', 'rpi3')
        self.assertEqual(arm_freq_rpi3.value, new_rpi3_val)
        self.assertEqual(arm_freq_rpi3.is_comment, False)

    def test_setting_commented_value(self):
        new_val = 1
        sdtv_mode = self.config.set('sdtv_mode', new_val)

        sdtv_mode = self.config.get('sdtv_mode')
        self.assertEqual(sdtv_mode.value, new_val)
        self.assertEqual(sdtv_mode.is_comment, True)

    def test_setting_compound_key(self):
        new_val = 'off'
        self.config.set('dtparam=i2c_arm', new_val)

        dtparam_mode = self.config.get('dtparam=i2c_arm')
        self.assertEqual(dtparam_mode.value, new_val)
        self.assertEqual(dtparam_mode.is_comment, False)

    def test_set_reset_value(self):
        new_val = 5
        new_edid_val = 7
        self.config.set('hdmi_group', new_val)
        self.config.set('hdmi_group', new_edid_val,
                        config_filter='EDID=VSC-TD2220')

        hdmi_group = self.config.get('hdmi_group')
        self.assertEqual(hdmi_group.value, new_val)
        self.assertEqual(hdmi_group.is_comment, False)

        warnings.warn(
            'Should the value set by `set` be the one controlled by the filter?'
        )
        hdmi_group_rpi3 = self.config.get('hdmi_group',
                                          config_filter='EDID=VSC-TD2220')
        self.assertEqual(hdmi_group_rpi3.value, new_edid_val)
        self.assertEqual(hdmi_group_rpi3.is_comment, False)
