#
# test_kano_safeboot_mode.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the kano_settings.commands.kano_safeboot_mode module.


import os


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
