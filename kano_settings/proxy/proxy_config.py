#!/usr/bin/env python
#
# proxy_config.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# A simple script to set Kanux behind a proxy.
# Files which are managed by this module are:
#
#  /etc/ld.so.preload
#  /etc/dante.conf
#

import os
from kano.utils import read_file_contents_as_lines


class LibPreload:
    def __init__(self, filename='/etc/ld.so.preload'):
        self.filename = filename
        self.libs = ['/usr/lib/libdsocksd.so.0', '/lib/arm-linux-gnueabihf/libdl.so.2']

    def is_enabled(self):
        # Reads through preload file in search of proxy libraries.
        # Supportes commented lines (# sign)
        if not os.path.exists(self.filename):
            return False
        with open(self.filename, "r") as infile:
            for line in infile:
                if line.strip('\n') in (self.libs):
                    return True
        return False

    # FIXME: This code shouts for a convenient refactoring
    # It does not work 100% as sometimes Chromium stalls. A restart sometimes solves the problem
    def chromium_proxy(self, ip, port, ptype, username, password, enable=True):
        chromium_cfg = '/etc/chromium/default'
        if enable:
            if 'socks_v5' in ptype:
                proxy_type = 'socks5'
            else:
                proxy_type = 'http'

            strflags = '"--password-store=detect --proxy-server="%s://%s:%s""' % (proxy_type, ip, port)
        else:
            strflags = '"--password-store=detect"'

        strflags = strflags.replace('/', '\/')
        cmd = "/bin/sed -i 's/CHROMIUM_FLAGS=.*/CHROMIUM_FLAGS=%s/g' %s" % (strflags, chromium_cfg)
        rc = os.system(cmd)
        return rc == 0

    def proxify(self, enable=False):

        # Chromium settings go to its config file. Change them now
        p = ProxySettings().get_settings()
        print 'setting chromium'
        self.chromium_proxy(p['proxy-ip'], p['proxy-port'], p['proxy-type'], None, None, enable)

        # If the change is already set, do nothing
        if enable == self.is_enabled():
            return True

        # Collect currently preloaded libraries
        entries = read_file_contents_as_lines(self.filename)

        # Add or remove proxy libraries
        if enable:
            for lib in self.libs:
                entries.append(lib)
        else:
            for l in self.libs:
                entries.remove(l + '\n')

        # Write back the prelaod file
        f = open(self.filename, 'w')
        for e in entries:
            if (e != '\n'):
                f.write("%s\n" % e)
        f.close()
        return True


class ProxySettings:
    def __init__(self, filename='/etc/dante.conf'):
        self.filename = filename
        self.marker = '# kano-settings - DO NOT TOUCH MANUALLY BELOW THIS LINE'

        self.dante_format_socks = \
            'route {\n' \
            '   from: 0.0.0.0/0   to: 0.0.0.0/0   via: %(proxy-ip)s port = %(proxy-port)s\n' \
            '   protocol: tcp udp\n' \
            '   proxyprotocol: socks_v4 socks_v5\n' \
            '}\n\n'

        self.dante_format_http = \
            'route {\n' \
            '   from: 0.0.0.0/0   to: 0.0.0.0/0   via: %(proxy-ip)s port = %(proxy-port)s\n' \
            '   command: connect\n' \
            '   proxyprotocol: http_v1.0\n' \
            '}\n\n'

    def parse_out(self, route_section):
        rs = route_section
        settings = {
            'proxy-ip': rs[1].split()[5],
            'proxy-port': rs[1].split()[8],
            'proxy-type': rs[3].split()[1:],
            'username': '',
            'password': ''
        }
        return settings

    def get_settings(self):
        saved_settings = None

        entries = read_file_contents_as_lines(self.filename)

        for c, e in enumerate(entries):
            if e.strip('\n') == self.marker:
                saved_settings = self.parse_out(entries[c + 1:])
        return saved_settings

    def set_settings(self, dict_settings):
        bmarker = False
        if dict_settings['proxy-type'] == 'http_v1.0':
            new_settings = self.dante_format_http % (dict_settings)
        else:
            new_settings = self.dante_format_socks % (dict_settings)

        # Read Dante's current settings
        entries = read_file_contents_as_lines(self.filename)

        # Override kano section with new settings
        f = open(self.filename, 'w')
        for c, e in enumerate(entries):
            f.write(e)
            if e.strip('\n') == self.marker:
                # Kano marker found, stop here to override new settings
                bmarker = True
                break

        if not bmarker:
            f.write(self.marker + '\n')

        f.write(new_settings)
        f.close()
        return True
