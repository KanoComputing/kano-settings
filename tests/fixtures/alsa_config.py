# alsa_config.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to facilitate working with the ALSA config file.


import pytest

from kano_settings.system.audio import DEFAULT_ALSA_CONFIG_MAX_DB, DEFAULT_CKC_V1_MAX_DB
from kano_settings.paths import ASOUND_CONF_PATH


ASOUND_CONF_PATTERN = ("""
pcm.master {{
    type softvol
    min_dB -26.0
    max_dB {max_dB}
    resolution 16

    slave {{
        pcm "hw:0"
    }}
    control {{
        name "Master"
        card 0
        count 1
    }}
}}

pcm.usb_mic {{
    type hw
    card 1
}}

pcm.!default {{
    type asym
    playback.pcm {{
        type plug
        slave.pcm "master"
    }}
    capture.pcm {{
        type plug
        slave.pcm "usb_mic"
    }}
}}
""")


DEFAULT_PARAMS = {
    'max_dB': DEFAULT_ALSA_CONFIG_MAX_DB,
}

CKC_V1_MAX_DB_PARAMS = {
    'max_dB': DEFAULT_CKC_V1_MAX_DB,
}

MAX_DB_VALUES = [4.0, -3.5432, 0]


@pytest.fixture(scope='function')
def asound_conf(fs, request):
    """
    A FakeFile object constructed with pyfakefs which contains the system
    ALSA configuration file.

    Python functions that operate on this file on the system will do so on
    this mocked file instead of the system file.
    """
    fake_asound_conf = fs.CreateFile(ASOUND_CONF_PATH)

    # Format the config pattern with all the items in the params dict and set
    # the fake file contents with that.
    fake_asound_conf.SetContents(ASOUND_CONF_PATTERN.format(**DEFAULT_PARAMS))

    yield fake_asound_conf

    # Clean up code, remove the file altogether.
    fs.RemoveFile(ASOUND_CONF_PATH)


@pytest.fixture(scope='function')
def asound_confs(asound_conf, max_dB_arg):
    """
    Sets up multiple fake ALSA configuration files with the use of asound_conf and
    max_dB_arg fixtures (add more as needed here).

    It is therefore a parameterised fixture which returns a dict object containing
    the FakeFile object and the parameters used in the configuration file.
    """
    config_params = DEFAULT_PARAMS.copy()
    config_params['max_dB'] = max_dB_arg

    # Format the config pattern with all the items in the params dict and set
    # the fake file contents with that.
    asound_conf.SetContents(ASOUND_CONF_PATTERN.format(**config_params))

    return {
        'fake_file': asound_conf,
        'params': config_params
    }


@pytest.fixture(scope='function', params=(MAX_DB_VALUES))
def max_dB_arg(request):
    """
    A parameterised fixture with all values that the ALSA config max_dB
    option might take.
    """
    return request.param
