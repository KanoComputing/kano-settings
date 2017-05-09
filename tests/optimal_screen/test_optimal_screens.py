#
# test_optimal_screens.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for bin/kano-settings-onboot
#
# Using a collection of screen information dumps from several screen models,
# the tests run the tool in test mode, and make sure the optimal resolutions
# are found and selected.
#
# To add more use cases, run "sudo kano-settings-onboot --dump > myscreen.dump"
# and add an additional test that checks for its optimal resolution / aspect ratio.
#
# TODO: Can these tests work inside the virtual QA sandbox?
#  @unittest.skipUnless('-rpi' in sys.argv, 'Skipping because this is not a real RPI')
#

import os
import sys
import unittest

# Import kano-settings from this cloned repository
sys.path.insert(1, '../../')

verbose = False
script_path = os.path.dirname(os.path.realpath(__file__))
app = 'sudo ' + os.path.join(script_path, '..', '..', 'bin', 'kano-settings-onboot')


class TestOptimalScreen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.system('sudo kano-logs config -l debug -o debug')

    @classmethod
    def tearDownClass(cls):
        os.system('sudo kano-logs config -l none -o none')

    def _test_dump(self, dumpfile):
        command = '{} --dry-run --verbose --force --test:{}'.format(app, dumpfile)
        output = os.popen(command).read()
        if verbose:
            print output
        return output

    def test_adafruit_hdmi(self):
        data = self._test_dump(os.path.join(script_path, 'screen-adafruit-hdmi.dump'))
        self.assertIn('Applying optimal mode', data)
        self.assertIn('changes applied: True', data)
        self.assertIn("u'resolution': u'1280x800', u'mode': 28, u'aspect': u'16:10'", data)


if __name__ == '__main__':
    verbose = os.getenv('VERBOSE')
    unittest.main()
