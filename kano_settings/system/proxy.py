#!/usr/bin/env python

# proxy.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from kano.utils import run_cmd

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


def set_all_proxies(enable, ip=None, port=None, username=None, password=None):
    set_chromium(enable, ip, port)


def get_all_proxies():
    return False, None
    # # data = get_dante()
    # if data:
    #     return True, data
    # else:
    #     return False, None

