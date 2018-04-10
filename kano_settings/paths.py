#
# paths.py
#
# Copyright (C) 2017 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# All the necessary paths used in this project.
#

from os.path import abspath, dirname, join


LOCAL_DIR = abspath(join(dirname(__file__), '..'))
BASE_DIR = '/usr/share/kano-settings'

# When running this project from a local clone, adapt the base installation path.
if not LOCAL_DIR.startswith(BASE_DIR):
    BASE_DIR = LOCAL_DIR

RESOURCES_DIR = join(BASE_DIR, 'res')
EDID_DIR = join(RESOURCES_DIR, 'edid')

RAW_EDID_DIR = join(EDID_DIR, 'raw')
RAW_EDID_NAME_PATTERN = '{filename}.edid'
RAW_EDID_PATH_PATTERN = join(RAW_EDID_DIR, RAW_EDID_NAME_PATTERN)

RPI_EDID_DUMPS_DIR = join(EDID_DIR, 'rpi_dumps')
RPI_EDID_DUMPS_PATH_PATTERN = join(RPI_EDID_DUMPS_DIR, '{filename}.dumps.json')

EDID_EXPECTED_DIR = join(EDID_DIR, 'expected')
EDID_EXPECTED_PATH_PATTERN = join(EDID_EXPECTED_DIR, '{filename}.expected.json')

TEST_TEMP_DIR = '.temp'

ASOUND_CONF_NAME = 'asound.conf'
ASOUND_CONF_BASE_PATH = '/etc'
ASOUND_CONF_PATH = join(ASOUND_CONF_BASE_PATH, ASOUND_CONF_NAME)

TMP_EDID_DAT_PATH = '/tmp/edid.dat'

SYSTEM_FLAGS_DIR = '/var/cache/kano-settings/'
CKC_V1_ONBOOT_VOLUME_FLAG = join(SYSTEM_FLAGS_DIR, 'ckc-v1-volume-lowered')
