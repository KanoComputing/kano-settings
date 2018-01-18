# test_display.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano_settings.system.display module.


import pytest

from tests.conftest import REASON_NOT_IMPLEMENTED


class TestDisplay(object):
    """
    Tests for the kano_settings.system.display module.
    """

    def test_get_edid_name(self, monkeypatch, edid):
        """
        Tests that the get_edid_name function returns the correct display model.

        Args:
            monkeypatch - pytest fixture which gives mocking functionality
            edid - parameterised fixture containing raw, rpi_dumps, expected test data
        """

        try:
            from kano_settings.system import display
        except RuntimeError as err:
            pytest.skip(
                'FIXME: RuntimeError: `kano_settings.system.display import ' \
                'fails randomly when Pytest decides to fiddle around with ' \
                'threads.\n{}'.format(err)
            )

        # Mock the run_cmd function such that it returns the dump for the device name.
        monkeypatch.setattr(
            display, 'run_cmd',
            lambda x: (edid['rpi_dumps']['device_name'], '', 0)
        )
        rv = display.get_edid_name(use_cached=False)

        assert(rv == edid['expected']['model'])

    def test_get_edid_name_cache(self, monkeypatch):
        """
        Tests that the get_edid_name function returns the correct cached values.

        It explicitly sets the cache for the function and mocks the "live" model such
        that if the cache isn't respected, it would return the "live" model.

        Args:
            monkeypatch - pytest fixture which gives mocking functionality
            edid - parameterised fixture containing raw, rpi_dumps, expected test data
        """

        from kano_settings.system import display

        cached_screen_name = 'CHACHE-SCR'
        live_screen_name = 'LIVE-SCR'

        # Mock the run_cmd function such that it returns the cached screen name and
        # call the function to explicitly set the cache.
        monkeypatch.setattr(
            display, 'run_cmd',
            lambda x: (cached_screen_name, '', 0)
        )
        display.get_edid_name(use_cached=False)

        # Mock the run_cmd function such that it returns the "live" screen name and
        # get the cached and live values from the function.
        monkeypatch.setattr(
            display, 'run_cmd',
            lambda x: (live_screen_name, '', 0)
        )
        rv_cache = display.get_edid_name(use_cached=True)
        rv_no_cache = display.get_edid_name(use_cached=False)

        assert(rv_cache == cached_screen_name and rv_no_cache == live_screen_name)

    def test_get_supported_modes(self, monkeypatch, edid, fs):
        """
        Tests the the get_supported_modes function returns the expected values.

        Args:
            monkeypatch - pytest fixture which gives mocking functionality
            edid - parameterised fixture containing raw, rpi_dumps, expected test data
        """

        from kano_settings.system import display

        # get_supported_modes will bail if it can't find the tvservice executable
        fs.CreateFile(display.tvservice_path)

        # Mock the subprocess function to return the dumps for the CEA modes.
        monkeypatch.setattr(
            display.subprocess, 'check_output',
            lambda x: edid['rpi_dumps']['cea_modes']
        )
        rv_cea = display.get_supported_modes('CEA', min_width=0, min_height=0)

        # Mock the subprocess function to return the dumps for the DMT modes.
        monkeypatch.setattr(
            display.subprocess, 'check_output',
            lambda x: edid['rpi_dumps']['dmt_modes']
        )
        rv_dmt = display.get_supported_modes('DMT', min_width=0, min_height=0)

        assert(
            rv_cea == edid['expected']['cea_modes'] and
            rv_dmt == edid['expected']['dmt_modes']
        )

    @pytest.mark.skip(REASON_NOT_IMPLEMENTED)
    def test_get_supported_modes_filtering(self):
        """
        Tests that the get_supported_modes function returns modes filtered with
        minimum width and height.
        """
        pass   # TODO: Implement this test.

    def test_list_supported_modes(self, monkeypatch, edid, fs):
        """
        Tests that the list_supported_modes function returns the expected values.

        Args:
            monkeypatch - pytest fixture which gives mocking functionality
            edid - parameterised fixture containing raw, rpi_dumps, expected test data
        """

        from kano_settings.system import display

        # get_supported_modes will bail if it can't find the tvservice executable
        fs.CreateFile(display.tvservice_path)

        # Mock the subprocess function to return the dumps for the CEA or DMT modes.
        monkeypatch.setattr(
            display.subprocess, 'check_output',
            lambda x: edid['rpi_dumps']['cea_modes'] if 'CEA' in x else edid['rpi_dumps']['dmt_modes']
        )
        rv = display.list_supported_modes(min_width=0, min_height=0, use_cached=False)

        assert(rv == edid['expected']['cea_modes'] + edid['expected']['dmt_modes'])

    @pytest.mark.skip(REASON_NOT_IMPLEMENTED)
    def test_list_supported_modes_filtering(self):
        """
        Tests that the list_supported_modes function returns modes filtered with
        minimum width and height.
        """
        pass  # TODO: Implement this test.

    @pytest.mark.skip(REASON_NOT_IMPLEMENTED)
    def test_list_supported_modes_cache(self):
        """
        Tests that the list_supported_modes function returns the correct cached values.
        """
        pass  # TODO: Implement this test.

    def test_compare_and_set_optimal_resolution(self, monkeypatch, edid):
        """
        Tests that the compare_and_set_optimal_resolution sets the optimal resolution.

        Args:
            monkeypatch - pytest fixture which gives mocking functionality
            edid - parameterised fixture containing raw, rpi_dumps, expected test data
        """

        from kano_settings.system import display

        set_mode = dict()

        def mock_set_hdmi_mode(group, mode):
            set_mode['group'] = group
            set_mode['mode'] = mode

        # Mock the get_optimal_resolution_mode function to return the expected optimal
        # mode (the test for that function's rv has it's own place).
        monkeypatch.setattr(
            display, 'get_optimal_resolution_mode',
            lambda x, y: edid['expected']['optimal_mode']
        )

        # Mock the set_hdmi_mode function to call a local definition of it (again, the
        # test for that function has it's own place and here we only test if it's called
        # with the correct parameters).
        monkeypatch.setattr(display, 'set_hdmi_mode', mock_set_hdmi_mode)

        mock_status = {
            'group': 'MOCK',
            'mode': 'MOCK'
        }
        display.compare_and_set_optimal_resolution(
            edid['expected']['edid'],
            mock_status,
            edid['expected']['cea_modes'] + edid['expected']['dmt_modes'],
            dry_run=False
        )

        # Assert that the set_hdmi_mode function would be called with the expected group
        # and mode values for the optimal display mode.
        assert(
            set_mode['group'] == edid['expected']['optimal_mode']['group'] and
            set_mode['mode'] == edid['expected']['optimal_mode']['mode']
        )

    def test_get_optimal_resolution_mode(self, monkeypatch, edid):
        """
        Tests that the get_optimal_resolution_mode function returns the expected values.

        Args:
            monkeypatch - pytest fixture which gives mocking functionality
            edid - parameterised fixture containing raw, rpi_dumps, expected test data
        """

        from kano_settings.system import display

        # As the function changes the dict inplace, make a copy to be safe.
        overriden_expected_edid = edid['expected']['edid'].copy()
        display.override_models(overriden_expected_edid, edid['expected']['model'])

        rv = display.get_optimal_resolution_mode(
            overriden_expected_edid,
            edid['expected']['cea_modes'] + edid['expected']['dmt_modes']
        )
        assert(rv == edid['expected']['optimal_mode'])

    def test_override_models(self, edid):
        """
        Tests that the override_models function sets all the options in the EDID.

        Args:
            edid - parameterised fixture containing raw, rpi_dumps, expected test data
        """

        from kano_settings.system import display

        # As the function changes the dict inplace, make a copy to be safe.
        overriden_expected_edid = edid['expected']['edid'].copy()
        display.override_models(overriden_expected_edid, edid['expected']['model'])

        if edid['expected']['model'] in display.EDID_OVERRIDES:
            # Check that the EDID now contains all the (key, value) pairs in the dict
            # that was used to change the values. The EDID is allowed to have more pairs,
            # but the ones matching by key must match in values.
            assert(
                overriden_expected_edid.viewitems() >=
                display.EDID_OVERRIDES[edid['expected']['model']].viewitems()
            )
        else:
            # Check that the EDID was not changed by the function when there are
            # no options to override.
            assert(overriden_expected_edid == edid['expected']['edid'])

    def test_set_safeboot_mode(self, screen_config):
        import kano_settings.system.display
        kano_settings.system.display.set_safeboot_mode()

        import kano_settings.boot_config
        kano_settings.boot_config.end_config_transaction()

        assert screen_config.get_line('hdmi_group', filtered=True).is_comment
        assert screen_config.get_line('hdmi_group', filtered=False).is_comment

        assert screen_config.get_line('hdmi_mode', filtered=True).is_comment
        assert screen_config.get_line('hdmi_mode', filtered=False).is_comment

        assert screen_config.get_line('hdmi_drive', filtered=True).is_comment
        assert screen_config.get_line('hdmi_drive', filtered=False).is_comment

    def test_set_safeboot_modes(self, screen_config, safe_mode):
        import kano_settings.system.display
        kano_settings.system.display.set_safeboot_mode(
            group=safe_mode.hdmi_group,
            mode=safe_mode.hdmi_mode
        )

        import kano_settings.boot_config
        kano_settings.boot_config.end_config_transaction()

        screen_config.check_key(
            'hdmi_group',
            val=safe_mode.hdmi_group,
            is_comment=not safe_mode.hdmi_group
        )
        screen_config.check_key(
            'hdmi_mode',
            val=safe_mode.hdmi_mode,
            is_comment=not safe_mode.hdmi_mode
        )
        screen_config.check_key('hdmi_drive', is_comment=True)

        hotplug = screen_config.get_line('hdmi_force_hotplug', filtered=True)
        assert not hotplug.is_comment
        assert hotplug.value == 1
