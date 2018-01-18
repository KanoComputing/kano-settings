#
# kano_keys_pressed.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to provide a fake implementation of kano-keys-pressed
#


import pytest


class HotkeySettings(object):
    def __init__(self, rv, label, hdmi_group=0, hdmi_mode=0,
                 comment_out=False, do_nothing=False):
        self.rv = rv
        self.label = label
        self.hdmi_group = hdmi_group
        self.hdmi_mode = hdmi_mode
        self.comment_out = comment_out
        self.do_nothing = do_nothing

    def __str__(self):
        return self.label


KEY_COMBOS = [
    HotkeySettings(-1, 'NO_HOTKEY', do_nothing=True),
    HotkeySettings(1, 'CTRL_ALT', comment_out=True),
    HotkeySettings(2, 'CTRL_ALT_1', hdmi_group=1, hdmi_mode=16),
    HotkeySettings(3, 'CTRL_ALT_7', hdmi_group=1, hdmi_mode=4)
]


@pytest.fixture(scope="function", params=KEY_COMBOS)
def kano_keys_pressed(request, fake_run_cmd):
    settings = request.param

    fake_run_cmd.register(
        r'kano-keys-pressed.*',
        lambda x: ('', None, settings.rv)
    )

    return settings
