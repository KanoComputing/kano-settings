# test_audio.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano_settings.system.audio module.


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

        from kano_settings.system import audio

        expected_line = 'max_dB {0:0.1f}'.format(max_dB_arg)

        # Call the function to be tested.
        audio.set_alsa_config_max_dB(max_dB_arg)

        # Read back the config file.
        asound_conf_lines = [line.strip() for line in asound_conf.contents.split('\n')]

        assert(expected_line in asound_conf_lines)

    def test_set_alsa_config_max_dB_valid_rv(self, asound_conf, DEFAULT_PARAMS):
        """
        Tests that the set_alsa_config_max_dB function reports correctly if
        there were changes made.

        Args:
            asound_conf - fake ALSA config file to mock the system file
        """

        from kano_settings.system import audio

        new_dB = 1234567

        # Call the function 3 times:
        #  1. With the value that is already set in the config => False (no changes)
        #  2. With a new value to set => True (changes were made)
        #  3. With the value from 2 again => False (no changes)
        no_changes_rv = audio.set_alsa_config_max_dB(DEFAULT_PARAMS['max_dB'])
        changes_rv = audio.set_alsa_config_max_dB(new_dB)
        second_no_changes_rv = audio.set_alsa_config_max_dB(new_dB)

        assert(not no_changes_rv and changes_rv and not second_no_changes_rv)

    def test_get_alsa_config_max_dB(self, asound_confs):
        """
        Tests that the get_alsa_config_max_dB function gets the correct value
        from the config file.

        The fixture used here does most of the work to trick the function to operate
        on different config files. It returns the value for max_dB with which the
        config was setup

        Args:
            asound_confs - fake ALSA config files with various max_dB values set
        """

        from kano_settings.system import audio

        assert(
            audio.get_alsa_config_max_dB() == asound_confs['params']['max_dB']
        )
