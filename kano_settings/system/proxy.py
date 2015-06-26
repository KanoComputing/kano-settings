#!/usr/bin/env python

# proxy.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This module is responsible for synchronizing proxy settings to Chromium, Midori, APT, Curl and Wget tools
#

import os
import requests
from kano.utils import run_cmd, get_all_home_folders, delete_file, \
    write_file_contents, read_file_contents_as_lines

chromium_cfg = '/etc/chromium/default'
midori_cfg = '/etc/xdg/midori/config'
apt_cfg = '/etc/apt/apt.conf.d/80proxy'


def set_all_proxies(enable, host=None, port=None, username=None, password=None):
    set_apt_proxy(enable, host, port, username, password)
    set_chromium(enable, host, port)
    set_midori(enable, host, port)
    set_curl(enable, host, port, username, password)
    set_wget(enable, host, port, username, password)


def get_all_proxies():
    return get_apt_proxy()


def generate_proxy_url(host=None, port=None, username=None, password=None):
    if username and password:
        string = 'http://{username}:{password}@{host}:{port}'.format(
            username=username, password=password, host=host, port=port)
    else:
        string = 'http://{host}:{port}'.format(
            host=host, port=port)

    return string


def set_chromium(enable, host=None, port=None):
    if enable:
        proxy_type = 'http'

        strflags = '"--password-store=detect --proxy-server="{}:\/\/{}:{}""'.format(proxy_type, host, port)
    else:
        strflags = '"--password-store=detect"'

    cmd = "/bin/sed -i 's/CHROMIUM_FLAGS=.*/CHROMIUM_FLAGS={}/g' {}".format(strflags, chromium_cfg)
    run_cmd(cmd)
    return


def set_midori(enable, host=None, port=None, user_agent='Mozilla/5.0 (X11; Linux) AppleWebKit/535.22+ Midori/0.4'):

    # Read Midori configuration file in
    with open(midori_cfg, 'r') as f:
        config_lines=f.readlines()

    def conf_add_or_replace(item, value, config_lines):
        '''
        A function to simplify editing the configuration file values
        add the item if not found, replace its value otherwise
        '''
        found=False
        newitem = '{}={}\n'.format(item, value)
        for idx, line in enumerate(config_lines):
            if line.startswith(item):
                config_lines[idx]=newitem
                found=True

        if not found:
            config_lines.append(newitem)

        return newitem

    def conf_remove(item, config_lines):
        '''
        Remove the configuration item from the configuration file
        '''
        removed=False
        for line in config_lines:
            if line.startswith(item):
                config_lines.remove(line)
                removed=True

        return removed

    if enable:
        conf_add_or_replace('proxy-type', 'MIDORI_PROXY_HTTP', config_lines)
        conf_add_or_replace('http-proxy', host, config_lines)
        conf_add_or_replace('http-proxy-port', port, config_lines)
        conf_add_or_replace('maximum-cache-size', '100', config_lines)
        conf_add_or_replace('identify-as', 'MIDORI_IDENT_GENUINE', config_lines)
        conf_add_or_replace('user-agent', user_agent, config_lines)
    else:
        conf_remove('proxy-type', config_lines)
        conf_remove('http-proxy', config_lines)
        conf_remove('http-proxy-port', config_lines)
        conf_remove('maximum-cache-size', config_lines)
        conf_remove('identify-as', config_lines)
        conf_remove('user-agent', config_lines)

    # Write the config file back to disk
    with open(midori_cfg, 'w') as f:
        f.writelines(config_lines)

    return


def set_curl(enable, host=None, port=None, username=None, password=None):
    url_string = generate_proxy_url(host, port, username, password)
    data = 'proxy={url}'.format(url=url_string)

    files = [os.path.join(f, '.curlrc') for f in get_all_home_folders(root=True, skel=True)]
    for f in files:
        if not enable:
            delete_file(f)
        else:
            write_file_contents(f, data)


def set_wget(enable, host=None, port=None, username=None, password=None):
    data = (
        'http_proxy=http://{host}:{port}/\n'
        'https_proxy=http://{host}:{port}/\n'
    ).format(host=host, port=port)

    if username and password:
        data += 'proxy_user={username}\n'.format(username=username)
        data += 'proxy_password={password}\n'.format(password=password)

    write_file_contents('/etc/wgetrc', data)


def get_apt_proxy():
    is_proxy = False
    proxy_url = None
    settings = {
        'username': None,
        'password': None,
        'host': None,
        'port': None
    }

    cfg = read_file_contents_as_lines(apt_cfg)

    if cfg:
        for line in cfg:
            if line.startswith('Acquire::'):
                url = line.split('//')[-1].replace('/";', '')

                if '@' in url:
                    credentials, socket = url.split('@')
                    settings['username'], settings['password'] = credentials.split(':')
                else:
                    socket = url

                settings['host'], settings['port'] = socket.split(':')
                is_proxy = True
                proxy_url = generate_proxy_url(
                    host=settings['host'], port=settings['port'],
                    username=settings['username'], password=settings['password']
                )

    return is_proxy, settings, proxy_url


def set_apt_proxy(enable, host=None, port=None, username=None, password=None):
    url_string = generate_proxy_url(host, port, username, password)

    if enable and host and port:
        cfg = 'Acquire::http::proxy "{url}/";'.format(url=url_string)
    else:
        cfg = ''

    write_file_contents(apt_cfg, cfg)


def get_requests_proxies():
    enabled, data, proxy_url = get_all_proxies()
    if not enabled:
        proxies = None
    else:
        proxies = {
            "http": "{}/".format(proxy_url),
            "https": "{}/".format(proxy_url),
        }

    return proxies


def test_proxy():
    try:
        response = requests.get('http://www.google.com/favicon.ico', proxies=get_requests_proxies())
        if response.ok:
            return True, None
        else:
            return False, response.reason
    except Exception:
        return False, 'Problem connecting to the proxy server'




