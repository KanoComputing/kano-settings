#!/usr/bin/env python

# proxy.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from kano.utils import run_cmd, get_all_home_folders, delete_file, \
    write_file_contents, chown_path

chromium_cfg = '/etc/chromium/default'


def set_chromium(enable, ip, port):
    if enable:
        proxy_type = 'http'

        strflags = '"--password-store=detect --proxy-server="%s:\/\/%s:%s""' % (proxy_type, ip, port)
    else:
        strflags = '"--password-store=detect"'

    cmd = "/bin/sed -i 's/CHROMIUM_FLAGS=.*/CHROMIUM_FLAGS=%s/g' %s" % (strflags, chromium_cfg)
    run_cmd(cmd)
    return


def set_curl(enable, host, port, username=None, password=None):
    if username and password:
        data = 'proxy=http://{username}:{password}@{host}:{port}'.format(
            username=username, password=password, host=host, port=port)
    else:
        data = 'proxy=http://{host}:{port}'.format(
            host=host, port=port)

    files = [os.path.join(f, '.curlrc') for f in get_all_home_folders(root=True)]
    for f in files:
        if not enable:
            delete_file(f)
        else:
            write_file_contents(f, data)
            chown_path(f)


def set_wget(enable, host, port, username=None, password=None):
    data = (
        'http_proxy=http://{host}:{port}/\n'
        'https_proxy=http://{host}:{port}/\n'
    ).format(host=host, port=port)

    if username and password:
        data += 'proxy_user={username}\n'.format(username=username)
        data += 'proxy_password={password}\n'.format(password=password)

    write_file_contents('/etc/wgetrc', data)


def set_all_proxies(enable, ip=None, port=None, username=None, password=None):
    set_chromium(enable, ip, port)


def get_all_proxies():
    return False, None
    # # data = get_dante()
    # if data:
    #     return True, data
    # else:
    #     return False, None

