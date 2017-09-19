# alsa_config.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to facilitate working with the ALSA config file.


import pytest

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


DEFAULT_MAX_DB = {
    'max_dB': 4.0,
}

CKC_MAX_DB = {
    'max_dB': -2.0,
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

    fake_asound_conf.SetContents(
        ASOUND_CONF_PATTERN.format(max_dB=DEFAULT_MAX_DB['max_dB'])
    )

    yield fake_asound_conf

    # Clean up code, remove the file altogether.
    fs.RemoveFile(ASOUND_CONF_PATH)


@pytest.fixture(scope='function', params=(MAX_DB_VALUES))
def max_dB_arg(request):
    """
    A parameterised fixture with all values that the ALSA config max_dB
    option might take.
    """
    return request.param
