# edid_data.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to provide a dataset of EDIDs.


import json
import pytest
from os import listdir
from os.path import basename

from kano_settings.paths import RAW_EDID_DIR, RAW_EDID_PATH_PATTERN, \
    RPI_EDID_DUMPS_PATH_PATTERN, EDID_EXPECTED_PATH_PATTERN


SCREEN_MODELS_WITH_MD5 = [
    raw_edid[:-len(basename(RAW_EDID_PATH_PATTERN.format(filename='')))]
    for raw_edid in listdir(RAW_EDID_DIR)
]


@pytest.fixture(scope='session')
def edid_loader(request):
    """
    A session fixture helper which loads a dataset of EDID data (from res/edid).
    The dataset was generated with tools/edid/generate-rpi-edid-dumps script.

    The return value is a dict containing 'raw', 'rpi_dumps', 'expected' data
    for each display in the dataset.
    """
    edid = dict()

    for model in SCREEN_MODELS_WITH_MD5:
        edid[model] = dict()

        raw_edid_path = RAW_EDID_PATH_PATTERN.format(filename=model)
        rpi_edid_dumps_path = RPI_EDID_DUMPS_PATH_PATTERN.format(filename=model)
        edid_expected_path = EDID_EXPECTED_PATH_PATTERN.format(filename=model)

        with open(raw_edid_path, 'r') as raw_edid_file:
            edid[model]['raw'] = raw_edid_file.read()

        with open(rpi_edid_dumps_path, 'r') as rpi_edid_dumps_file:
            edid[model]['rpi_dumps'] = json.load(rpi_edid_dumps_file)

        with open(edid_expected_path, 'r') as edid_expected_file:
            edid[model]['expected'] = json.load(edid_expected_file)

    yield edid


@pytest.fixture(scope='function', params=(SCREEN_MODELS_WITH_MD5))
def edid(request, edid_loader):
    """
    A parameterised fixture for each screen in the dataset which contains
    the raw EDID, dumps from RPi, and expected data models from functions.

    The return value is a dict with the following structure:
    {
        'raw': str (file contents of res/edid/raw/*)
        'rpi_dumps': dict (file contents of res/edid/rpi_dumps/*)
        'expected': dict (file contents of res/edid/expected/*)
    }
    """
    yield edid_loader[request.param]
