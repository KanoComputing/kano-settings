#
# tools.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Useful functions for testing
#


import os
import shutil
from contextlib import contextmanager

def test_print(s):
    print '\n        ........{}'.format(s)


@contextmanager
def mock_file(file_path, mock_data=None):
    original_file = file_path + '.orig'

    if os.path.exists(file_path):
        shutil.move(file_path, original_file)

    if mock_data:
        with open(file_path, 'w') as mock_file_handle:
            mock_file_handle.write(mock_data)

    yield

    if os.path.exists(file_path):
        os.remove(file_path)

    if os.path.exists(original_file):
        shutil.move(original_file, file_path)
