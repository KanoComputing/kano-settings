#
# run_cmd.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to provide a fake implementation of run_cmd
#


import re
import pytest


@pytest.fixture(scope='function')
def fake_run_cmd(monkeypatch):
    '''
    Overrides the run_cmd function provided by `kano.utils.shell` to permit
    fake system calls. This function often needs to be overwritten multiple
    times to allow multiple inputs, to allow this supply a register() function
    '''

    cmds = [
    ]

    def mock_run_cmd(cmd):
        for regex, cb in cmds:
            if regex.match(cmd):
                return cb(cmd)

        raise NotImplementedError(
            'run_cmd called with unsupported argument: run_cmd({})'.format(cmd)
        )

    def register(regex, cb):
        '''
        Arguments
        ---------

        regex: str
            A regular expression string (which will be compiled with
            `re.compile()`) to use to match the command
        cb: fn(str)
            A callback function to be triggered when the regex matches
        '''

        cmds.insert(
            0, (re.compile(regex), cb)
        )

    import kano.utils.shell
    monkeypatch.setattr(kano.utils.shell, 'run_cmd', mock_run_cmd)
    monkeypatch.register = register

    return monkeypatch
