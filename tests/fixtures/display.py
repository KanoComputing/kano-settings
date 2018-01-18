#
# display.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to provide a fake implementation of display functions
#


import pytest


@pytest.fixture(scope="function")
def fake_get_edid_name(edid, monkeypatch):
    def get_edid_name(use_cached=True):
        return edid['rpi_dumps']['device_name'].strip('device_name=').rstrip()

    import kano_settings.system.display
    monkeypatch.setattr(
        kano_settings.system.display,
        'get_edid_name',
        get_edid_name
    )

    return get_edid_name()
