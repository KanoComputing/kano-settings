#!/usr/bin/env python

# proxy.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from string import Template
from kano.utils import read_file_contents_as_lines, write_file_contents, run_cmd

chromium_cfg = '/etc/chromium/default'
dante_conf = '/etc/dante.conf'
ld_so_preload_file = '/etc/ld.so.preload'
ld_so_preload_libs = ['/usr/lib/libdsocksd.so.0', '/lib/arm-linux-gnueabihf/libdl.so.2']

template_dante_socks = Template("""
# kano-settings generated dante.conf

route {
   from: 0.0.0.0/0   to: 0.0.0.0/0   via: $proxyip port = $proxyport
   protocol: tcp udp
   proxyprotocol: socks_v4 socks_v5
}
""")

template_dante_http = Template("""
# kano-settings generated dante.conf

route {
   from: 0.0.0.0/0   to: 0.0.0.0/0   via: $proxyip port = $proxyport
   command: connect
   proxyprotocol: http_v1.0
}
""")


def set_chromium(enable, ip, port, is_socks):
    if enable:
        if is_socks:
            proxy_type = 'socks5'
        else:
            proxy_type = 'http'

        strflags = '"--password-store=detect --proxy-server="%s:\/\/%s:%s""' % (proxy_type, ip, port)
    else:
        strflags = '"--password-store=detect"'

    cmd = "/bin/sed -i 's/CHROMIUM_FLAGS=.*/CHROMIUM_FLAGS=%s/g' %s" % (strflags, chromium_cfg)
    run_cmd(cmd)
    return


def set_dante(enable, proxyip, proxyport, is_socks):
    if enable:
        if is_socks:
            new_settings = template_dante_socks.substitute({'proxyip': proxyip, 'proxyport': proxyport})
        else:
            new_settings = template_dante_http.substitute({'proxyip': proxyip, 'proxyport': proxyport})
    else:
        new_settings = ''

    write_file_contents(dante_conf, new_settings)
    update_ld_so_preload(enable)


def get_dante():
    lines = read_file_contents_as_lines(dante_conf)
    if not lines:
        return

    proxyip = proxyport = is_socks = None
    try:
        for line in lines:
            if line.startswith('from:'):
                proxyip = line.split('via: ')[1].split()[0]
                proxyport = line.split('port = ')[1].split()[0]

            if line.startswith('proxyprotocol:'):
                proxytype = line.split()[1:]
                is_socks = 'socks' in proxytype[0]
    except Exception:
        return

    if not (proxyip or proxyport or is_socks):
        return
    else:
        return proxyip, proxyport, is_socks


def update_ld_so_preload(enable):
    lines = read_file_contents_as_lines(ld_so_preload_file)

    # remove existing modules
    if not enable:
        new_file = [l for l in lines if l not in ld_so_preload_libs]

    # add module if not found
    else:
        if not lines:
            new_file = ld_so_preload_libs
        else:
            new_file = lines + [l for l in ld_so_preload_libs if l not in lines]

    write_file_contents(ld_so_preload_file, '\n'.join(new_file))


def set_all_proxies(enable, ip=None, port=None, is_socks=None, username=None, password=None):
    set_chromium(enable, ip, port, is_socks)
    set_dante(enable, ip, port, is_socks)


def get_all_proxies():
    data = get_dante()
    if data:
        return True, data
    else:
        return False, None

