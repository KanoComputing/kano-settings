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
        self.chromium_cfg = '/etc/chromium/default'

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
    def set_chromium_proxy(self, ip, port, ptype, username, password, enable=True):
        if enable:
            if 'socks_v5' in ptype:
                proxy_type = 'socks5'
            else:
                proxy_type = 'http'

            strflags = '"--password-store=detect --proxy-server="%s://%s:%s""' % (proxy_type, ip, port)
        else:
            strflags = '"--password-store=detect"'

        strflags = strflags.replace('/', '\/')
        cmd = "/bin/sed -i 's/CHROMIUM_FLAGS=.*/CHROMIUM_FLAGS=%s/g' %s" % (strflags, self.chromium_cfg)
        rc = os.system(cmd)
        return rc == 0

    def proxify(self, enable=False):

        # Chromium settings go to its config file. Change them now
        p = ProxySettings().get_settings()
        if not p:
            print 'error setting chromium proxy'
            return

        print 'setting chromium'
        self.set_chromium_proxy(p['proxy-ip'], p['proxy-port'], p['proxy-type'], None, None, enable)

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
        self.chromium_cfg = '/etc/chromium/default'

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

        # collect and return Chromium proxy settings
        # TODO: Refactor code so we centralize set / get chromium settings
        try:
            r = open(self.chromium_cfg).readlines()
            for j in r:
                p = j.find('--proxy-server')
                if (p != -1):
                    # I know... below code hurts my eyes too...
                    # What we are breaking down is a string in the following form:
                    # CHROMIUM_FLAGS="--password-store=detect --proxy-server="socks5://10.5.5.5:9999"\n
                    if saved_settings is None:
                        saved_settings = {}

                    keys = j[p:].partition(':')
                    socks_type = keys[0].split('=')[1].strip('"')
                    socks_ip = keys[2].split(':')[0].strip('//')
                    socks_port = keys[2].split(':')[1].strip('"\n')

                    saved_settings['chromium_type'] = socks_type
                    saved_settings['chromium_ip'] = socks_ip
                    saved_settings['chromium_port'] = socks_port
        except:
            # Chromium does not have proxy settings
            pass

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
