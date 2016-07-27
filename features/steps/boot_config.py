from behave import *
import mock
from decorator import decorator

from boot_config_constants import RESOLUTIONS
import kano_settings.boot_config as boot_config
import kano_settings.system.display as display


@decorator
def create_config(func, ctx, *args, **kwargs):
    if not hasattr(ctx, 'config_file'):
        print('creating config')
        ctx.config_file_path = 'tmp_config.txt'
        ctx.config_file = boot_config.BootConfig(path=ctx.config_file_path)
    else:
        print('config already done')

    func(ctx, *args, **kwargs)

    # TODO: Implement creation and tear down


@given('A screen with EDID "{edid}" is plugged in')
@create_config
def setup_screen_edid(ctx, edid):
    # return

    '''
    real_config = BootConfig()
    pi1_backup_config = BootConfig(boot_config_pi1_backup_path)
    pi2_backup_config = BootConfig(boot_config_pi2_backup_path)
    '''

    raise NotImplementedError(
        u'STEP: Given A screen with EDID "{edid}" is plugged in'
        .format(edid=edid)
    )

@given('The resolution is {res}')
@create_config
def setup_resolution(ctx, res):
    return
    raise NotImplementedError(
        u'STEP: Given The resolution is {res}'.format(res=res)
    )

@when('The resolution is set to {res}')
def set_resolution(ctx, res):
    assert res in RESOLUTIONS

    res_data = RESOLUTIONS.get(res)

    if not res_data:
        assert False

    with mock.patch('kano_settings.boot_config.real_config', ctx.config_file):
        display.set_hdmi_mode(group=res_data['group'], mode=res_data['mode'])


@then('Only the EDID "{edid}" entry is changed')
def ensure_only_change(ctx, edid):
    return

    raise NotImplementedError(
        u'STEP: Then Only the EDID "{edid}" entry is changed'.format(edid=edid)
    )
