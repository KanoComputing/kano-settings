#
# boot_config.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to provide a fake /boot/config.txt file
#


import os
import pytest


BOOT_CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'boot_config'
)
BOOT_CONFIG_FILE = os.path.join(BOOT_CONFIG_DIR, 'config.txt')
with open(BOOT_CONFIG_FILE, 'r') as boot_conf_f:
    BASE_BOOT_CONFIG_DATA = boot_conf_f.read()


@pytest.fixture(scope='function')
def fake_open_locked(fs, monkeypatch):
    '''
    A version of the `open_locked()` function provided by
    `kano.utils.file_operations` which works with the fake fs. It simply
    ignores all non-standard options and passes the request on to the fake fs's
    implementation of `open()`
    '''

    import kano.utils.file_operations

    def open_locked(*args, **kwargs):
        '''
        Strip out options unsupported by pyfakefs
        '''
        if kwargs.get('nonblock') is not None:
            del kwargs['nonblock']

        if kwargs.get('timeout'):
            del kwargs['timeout']

        return open(*args, **kwargs)

    monkeypatch.setattr(
        kano.utils.file_operations,
        'open_locked',
        open_locked
    )


@pytest.fixture(scope='function')
def boot_config(fs, monkeypatch, fake_open_locked):
    '''
    A fake `/boot/config.txt` file which can be manipulated and verified on any
    platform by using a fake fs.

    There are two helper functions attached to the returned object:

    set_value()
        Parameters
        ----------
        setting : str
            Name of the config.txt option to set
        val : str
            Value to set the option to
        config_filter : str, optional
            Config filter to use

    get_value()
        Parameters
        ----------
        setting : str
            Name of the config.txt option to set
        config_filter : str, optional
            Config filter to use
        fallback : bool, optional
            Whether to fallback to use no filter if the filter isn't found

        Returns
        -------
        str
            Value the option has been set to
    '''

    from kano_settings.system.boot_config.boot_config_filter import Filter

    conf_f = fs.CreateFile('/boot/config.txt', contents=BASE_BOOT_CONFIG_DATA)
    fs.CreateDirectory('/run/lock')

    # As part of the ConfigTransaction.close() method, an os.system('sync') is
    # called, mock this as it will fail to do as advertised
    def fake_os_system(cmd):
        if cmd != 'sync':
            raise NotImplementedError(
                'os.system not called with "sync": os.system({})'.format(cmd)
            )
    monkeypatch.setattr(os, 'system', fake_os_system)

    def set_values(settings):
        '''
        Helper function for initialising the boot config to the desired state
        '''

        from kano_settings.system.boot_config.boot_config_parser import \
            BootConfigParser

        with open('/boot/config.txt', 'r') as conf_f:
            conf = BootConfigParser(conf_f.readlines())

        for setting in settings:
            key = setting[0]
            val = setting[1]

            if len(setting) == 3:
                config_filter = setting[2]
            else:
                config_filter = Filter.ALL

            conf.set(key, val, config_filter=config_filter)

        with open('/boot/config.txt', 'w') as conf_f:
            conf_f.write(conf.dump())

    def get_conf():
        '''
        Helper function for checking what the config file looks like after
        edits
        '''

        from kano_settings.system.boot_config.boot_config_parser import \
            BootConfigParser

        with open('/boot/config.txt', 'r') as conf_f:
            conf = BootConfigParser(conf_f.readlines())

        return conf

    conf_f.set_values = set_values
    conf_f.get_conf = get_conf

    return conf_f


@pytest.fixture(scope='function')
def screen_config(boot_config, fake_get_edid_name):
    '''
    '''

    from kano_settings.system.boot_config.boot_config_filter import Filter

    device_id = fake_get_edid_name
    conf_filter = Filter.get_edid_filter(device_id)

    boot_config.set_values((
        # hdmi_mode
        ('hdmi_mode', 845, Filter.ALL),
        ('hdmi_mode', 216, conf_filter),

        # hdmi_group
        ('hdmi_group', 432, Filter.ALL),
        ('hdmi_group', 112, conf_filter),

        # hdmi_drive
        ('hdmi_drive', 123, Filter.ALL),
        ('hdmi_drive', 321, conf_filter),
    ))

    def get_line(key, filtered=True):
        if filtered:
            filter_val = conf_filter
            fallback = False
        else:
            filter_val = Filter.ALL
            fallback = True

        return boot_config.get_conf().get_line(
            key, config_filter=filter_val, fallback=fallback
        )

    def check_key(key, val=0, is_comment=False):
        line_filtered = get_line(key, filtered=True)
        assert line_filtered.is_comment == is_comment
        if not is_comment:
            assert line_filtered.value == val

        line_unfiltered = get_line(key, filtered=False)
        assert line_unfiltered.is_comment == is_comment
        if not is_comment:
            assert line_unfiltered.value == val

    boot_config.edid_filter = conf_filter
    boot_config.get_line = get_line
    boot_config.check_key = check_key

    return boot_config


class SafebootModeOption(object):
    def __init__(self, group, mode, label):
        self.hdmi_group = group
        self.hdmi_mode = mode
        self.label = label

    def __str__(self):
        return '{} safeboot'.format(self.label)


SAFE_MODE_PARAMS = (
    SafebootModeOption(None, None, "Native"),
    SafebootModeOption(1, 4, "720p"),
    SafebootModeOption(1, 16, "1080p"),
)


@pytest.fixture(scope='module', params=SAFE_MODE_PARAMS, ids=lambda x: str(x))
def safe_mode(request):
    return request.param
