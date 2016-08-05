from behave import *

try:
    import unittest.mock as mock  # Moved in Python 3
except ImportError:
    import mock

from decorator import decorator

import pyfakefs.fake_filesystem as fake_fs

from steps.boot_config_constants import RESOLUTIONS, BASE_CONFIG_FILE, \
    BOOT_CONFIG_FILEPATH
from steps.diff import Diff


with mock.patch('atexit.register'):
    import kano_settings.boot_config as boot_config


import pyfakefs.fake_filesystem as fake_fs

def get_fake_fs():
    fs = fake_fs.FakeFilesystem()
    fs.CreateDirectory('/usr/share/kano-settings/media')

    return fs


with mock.patch('os.path', spec=fake_fs.FakeOsModule(get_fake_fs())):
    import kano_settings.system.display as display


@decorator
def create_config(func, ctx, *args, **kwargs):
    # ctx.patcher.fs.CreateFile('/boot/config.txt')
    '''
    if not hasattr(ctx, 'config_file'):
        print('creating config')
        ctx.config_file_path = 'tmp_config.txt'
        ctx.config_file = boot_config.BootConfig(path=ctx.config_file_path)
    else:
        print('config already done')
    '''

    func(ctx, *args, **kwargs)

    # TODO: Implement creation and tear down


@given('A screen with EDID "{edid}" is plugged in')
def setup_screen_edid(ctx, edid):
    import kano_settings.boot_config as boot_config
    ctx.edid = edid

def get_display_config(res):
    assert res in RESOLUTIONS

    res_data = RESOLUTIONS.get(res)

    if not res_data:
        assert False

    group = res_data.get('group')
    mode = res_data.get('mode')

    return {
        'group_line': 'hdmi_group={group}'.format(group=group),
        'mode_line': 'hdmi_mode={mode}'.format(mode=mode),
        'group': group,
        'mode': mode
    }


def get_edid_filter(edid):
    if not edid:
        return ''

    return '[EDID={edid}]'.format(edid=edid)


@given('The resolution is {res}')
def setup_resolution(ctx, res):
    res_data = get_display_config(res)
    ctx.original_res = res_data

    with open(BOOT_CONFIG_FILEPATH, 'a') as f:
        f.write('{}\n'.format(get_edid_filter(ctx.edid)))
        f.write('{}\n'.format(res_data.get('group_line')))
        f.write('{}\n'.format(res_data.get('mode_line')))


@when('The resolution is set to {res}')
def set_resolution(ctx, res):
    res_data = get_display_config(res)
    ctx.new_res = res_data

    '''
    # FIXME: Don't do this manually
    with open(BOOT_CONFIG_FILEPATH, 'a') as f:
        f.write('{}\n'.format(res_data.get('group_line')))
        f.write('{}\n'.format(res_data.get('mode_line')))
    '''


    display.set_hdmi_mode(group=res_data['group'], mode=res_data['mode'])
    with mock.patch('os.open'):
        with mock.patch('pyfakefs.fake_filesystem.FakeOsModule.open', spec=fake_fs.FakeOsModule.open) as fake_open:
            print(fake_open)
            boot_config.end_config_transaction()



@then('Only the EDID "{edid}" entry is changed')
def ensure_only_change(ctx, edid):
    with open(BOOT_CONFIG_FILEPATH, 'r') as f:
        new_boot_config = f.readlines()

    original_fs = fake_fs.FakeFileOpen(ctx.backup_fs)
    original_boot_config = [l for l in original_fs(BOOT_CONFIG_FILEPATH)]

    diff = Diff(original_boot_config, new_boot_config)

    assert ctx.new_res.get('mode_line') in diff.added
    assert ctx.original_res.get('mode_line') in diff.removed
