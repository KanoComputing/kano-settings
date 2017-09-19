# test_audio.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano_settings.system.audio module.


from kano_settings.system import audio

from tests.fixtures.alsa_config import DEFAULT_MAX_DB


class TestAudio(object):
    """
    Tests for the kano_settings.system.audio module.
    """

    def test_set_alsa_config_max_dB_valid(self, asound_conf, max_dB_arg):
        """
        Tests that the set_alsa_config_max_dB function sets the
        config file as expected.

        Args:
            asound_conf - fake ALSA config file to mock the system file
            max_dB_arg - parameterised fixture containing max_dB values
        """
        expected_line = 'max_dB {0:0.1f}'.format(max_dB_arg)

        # Call the function to be tested.
        audio.set_alsa_config_max_dB(max_dB_arg)

        # Read back the config file.
        asound_conf_lines = [line.strip() for line in asound_conf.contents.split('\n')]

        assert(expected_line in asound_conf_lines)

    def test_set_alsa_config_max_dB_valid_rv(self, asound_conf):
        """
        Tests that the set_alsa_config_max_dB function reports correctly if
        there were changes made.

        Args:
            asound_conf - fake ALSA config file to mock the system file
        """
        new_dB = 1234567

        # Call the function 3 times:
        #  1. With the value that is already set in the config => False (no changes)
        #  2. With a new value to set => True (changes were made)
        #  3. With the value from 2 again => False (no changes)
        no_changes_rv = audio.set_alsa_config_max_dB(DEFAULT_MAX_DB['max_dB'])
        changes_rv = audio.set_alsa_config_max_dB(new_dB)
        second_no_changes_rv = audio.set_alsa_config_max_dB(new_dB)

        assert(not no_changes_rv and changes_rv and not second_no_changes_rv)
