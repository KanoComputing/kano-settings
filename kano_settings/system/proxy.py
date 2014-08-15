#!/usr/bin/env python

# proxy.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#


from kano.utils import read_file_contents_as_lines
from kano.logging import logger
from kano.utils import get_user_unsudoed, run_bg, run_cmd

chromium_cfg = '/etc/chromium/default'
dante_conf = '/etc/dante.conf'
ld_so_preload_file = '/etc/ld.so.preload'
ld_so_preload_libs = ['/usr/lib/libdsocksd.so.0', '/lib/arm-linux-gnueabihf/libdl.so.2']

template_dante_socks = """
# kano-settings generated dante.conf

route {
   from: 0.0.0.0/0   to: 0.0.0.0/0   via: %(proxy-ip)s port = %(proxy-port)s
   protocol: tcp udp
   proxyprotocol: socks_v4 socks_v5
}
"""

template_dante_http = """
# kano-settings generated dante.conf

route {
   from: 0.0.0.0/0   to: 0.0.0.0/0   via: %(proxy-ip)s port = %(proxy-port)s
   command: connect
   proxyprotocol: http_v1.0
}
"""


def set_chromium_proxy(ip, port, ptype, username, password, enable=True):
    if enable:
        if 'socks_v5' in ptype:
            proxy_type = 'socks5'
        else:
            proxy_type = 'http'

        strflags = '"--password-store=detect --proxy-server="%s:\/\/%s:%s""' % (proxy_type, ip, port)
    else:
        strflags = '"--password-store=detect"'

    cmd = "/bin/sed -i 's/CHROMIUM_FLAGS=.*/CHROMIUM_FLAGS=%s/g' %s" % (strflags, chromium_cfg)
    _, _, rc = run_cmd(cmd)
    return rc == 0


def get_chromium_proxy():
    lines = read_file_contents_as_lines(chromium_cfg)
    for line in lines:
        if '--proxy-server' in line:
            return True


def lib_preload_is_enabled():
    enabled_modules = read_file_contents_as_lines(ld_so_preload_file)
    for module in enabled_modules:
        if module in ld_so_preload_libs:
            return True
    return False


class LibPreload:

    def proxify(self, enable=False):

        # Chromium settings go to its config file. Change them now
        p = ProxySettings().get_settings()
        if not p:
            logger.error('error setting chromium proxy')
            return

        logger.info('setting chromium')
        set_chromium_proxy(p['proxy-ip'], p['proxy-port'], p['proxy-type'], None, None, enable)

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





def parse_out(rs):
    settings = {
        'proxy-ip': rs[1].split()[5],
        'proxy-port': rs[1].split()[8],
        'proxy-type': rs[3].split()[1:],
        'username': '',
        'password': ''
    }
    return settings


def get_settings():
    saved_settings = None

    entries = read_file_contents_as_lines(dante_conf)
    if not entries:
        return

    parse_out(entries)
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



def is_enabled():
    return libpreload.is_enabled()


def enable():
    libpreload.proxify(True)


def disable():
    libpreload.proxify(False)


def set_settings(proxyip, proxyport, proxytype, username=None, password=None):
    settings = {
        'proxy-ip': proxyip,
        'proxy-port': proxyport,
        'proxy-type': proxytype,   # one of : "socks_v4 socks_v5" or "http_v1.0"
        'username': username,
        'password': password
    }
    pxysettings.set_settings(settings)


def get_settings():
    return pxysettings.get_settings()


def launch_chromium(widget=None, event=None):
    user_name = get_user_unsudoed()
    run_bg('su - ' + user_name + ' -c chromium')


def network_info():
    network = ''
    command_ip = ''
    command_network = '/sbin/iwconfig wlan0 | grep \'ESSID:\' | awk \'{print $4}\' | sed \'s/ESSID://g\' | sed \'s/\"//g\''
    out, e, _ = run_cmd(command_network)
    if e:
        network = "Ethernet"
        command_ip = '/sbin/ifconfig eth0 | grep inet | awk \'{print $2}\' | cut -d\':\' -f2'
    else:
        network = out
        command_ip = '/sbin/ifconfig wlan0 | grep inet | awk \'{print $2}\' | cut -d\':\' -f2'
    ip, _, _ = run_cmd(command_ip)

    return [network.rstrip(), ip.rstrip()]


