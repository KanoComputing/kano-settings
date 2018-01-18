#
# test_kano_safeboot_mode.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano_settings.commands.kano_safeboot_mode module.
#


import os
import imp
import pytest


def test_get_requested_safe_mode(fs, kano_keys_pressed, boot_config):
    try:
        import kano_settings.commands.kano_safeboot_mode as kano_safeboot_mode
        imp.reload(kano_safeboot_mode)
    except RuntimeError as err:
        pytest.skip(
            'FIXME: RuntimeError: `kano_settings.commands.kano_safeboot_mode '
            'import fails randomly when Pytest decides to fiddle around with '
            'threads.\n{}'.format(err)
        )

    assert kano_safeboot_mode.get_requested_safe_mode() == kano_keys_pressed.rv


def test_set_safeboot_token(fs):
    import kano_settings.commands.kano_safeboot_mode as kano_safeboot_mode

    assert not os.path.exists(kano_safeboot_mode.TOKEN_FILENAME)

    kano_safeboot_mode.set_safeboot_token()

    assert os.path.exists(kano_safeboot_mode.TOKEN_FILENAME)


def test_is_token_set(fs):
    import kano_settings.commands.kano_safeboot_mode as kano_safeboot_mode

    assert not kano_safeboot_mode.is_token_set()

    fs.CreateFile(kano_safeboot_mode.TOKEN_FILENAME)

    assert kano_safeboot_mode.is_token_set()


def test_remove_token(fs):
    import kano_settings.commands.kano_safeboot_mode as kano_safeboot_mode

    fs.CreateFile(kano_safeboot_mode.TOKEN_FILENAME)

    kano_safeboot_mode.remove_token()

    assert not os.path.exists(kano_safeboot_mode.TOKEN_FILENAME)


def test_kano_safeboot_mode_main(monkeypatch, screen_config, kano_keys_pressed,
                                 fake_run_cmd):
    import kano_settings.boot_config
    monkeypatch.setattr(kano_settings.boot_config, 'enforce_pi', lambda: None)

    import kano.utils.user
    monkeypatch.setattr(kano.utils.user, 'enforce_root', lambda x: None)

    fake_run_cmd.register(
        'kano-checked-reboot safeboot systemctl reboot.*',
        lambda x: None
    )

    import kano_settings.commands.kano_safeboot_mode as kano_safeboot_mode
    imp.reload(kano_safeboot_mode)
    kano_safeboot_mode.main()

    if kano_keys_pressed.do_nothing:
        # There should have been no modifications
        with open('/boot/config.txt', 'r') as conf_f:
            assert screen_config.contents == conf_f.read()

        return

    screen_config.check_key(
        'hdmi_group',
        val=kano_keys_pressed.hdmi_group,
        is_comment=kano_keys_pressed.comment_out
    )
    screen_config.check_key(
        'hdmi_mode',
        val=kano_keys_pressed.hdmi_mode,
        is_comment=kano_keys_pressed.comment_out
    )
    screen_config.check_key('hdmi_drive', is_comment=True)

    hotplug = screen_config.get_line('hdmi_force_hotplug', filtered=True)
    assert not hotplug.is_comment
    assert hotplug.value == 1
