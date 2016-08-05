import copy

try:
    import unittest.mock as mock  # Moved in Python 3
except ImportError:
    import mock

from behave import *
from decorator import decorator
from pyfakefs.fake_filesystem_unittest import Patcher

from steps.boot_config_constants import RESOLUTIONS, BASE_CONFIG_FILE, \
    BOOT_CONFIG_FILEPATH

FAKE_FS = None

@decorator
def refresh_fs(func, ctx, *args, **kwargs):
    print('creating fs')
    if not hasattr(ctx, 'patcher') or not ctx.patcher:
        ctx.patcher = FAKE_FS
        ctx.fs = ctx.patcher.fs

        # TODO: Move
        ctx.patcher.fs.CreateFile(
            BOOT_CONFIG_FILEPATH,
            contents=BASE_CONFIG_FILE
        )
        ctx.patcher.fs.CreateDirectory('/usr/share/kano-settings/media')
        ctx.patcher.fs.CreateDirectory('/run/lock')

    return func(ctx, *args, **kwargs)


def backup_fs(ctx):
    ctx.backup_fs = copy.deepcopy(ctx.patcher.fs)


@decorator
def destroy_fs(func, ctx, *args, **kwargs):
    if hasattr(ctx, 'patcher'):
        print('destroying fs')
        ctx.patcher.tearDown()
        # FIXME
        ctx.patcher = None

    return func(ctx, *args, **kwargs)


def before_all(dummy_ctx):
    from steps.fs import FAKE_FS
    pass


def before_feature(dummy_ctx, dummy_feature):
    pass


@refresh_fs
def before_scenario(ctx, dummy_scenario):
    ctx.edid = None


# @destroy_fs
def after_scenario(dummy_ctx, dummy_scenario):
    pass


def after_step(ctx, step):
    if step.step_type == 'given':
        backup_fs(ctx)


def after_feature(dummy_ctx, dummy_feature):
    pass


@destroy_fs
def after_all(dummy_ctx):
    pass
