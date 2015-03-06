#!/usr/bin/env python

# advanced.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Contains the advanced backend functions


import os
import shutil
import hashlib
import subprocess
import signal

from kano_settings.common import settings_dir
from kano.utils import read_file_contents, write_file_contents, \
    read_file_contents_as_lines, read_json, write_json, ensure_dir, \
    get_user_unsudoed
from kano.logging import logger
from kano.network import set_dns, restore_dns_interfaces, \
    clear_dns_interfaces, refresh_resolvconf

password_file = "/etc/kano-parental-lock"
hosts_file = '/etc/hosts'
chromium_policy_file = '/etc/chromium/policies/managed/policy.json'
sentry_config = '/usr/share/kano-settings/config/sentry'

username = get_user_unsudoed()

# TODO: is this needed?
if username != 'root':
    blacklist_file = os.path.join(settings_dir, 'blacklist')
    whitelist_file = os.path.join(settings_dir, 'whitelist')


def get_parental_enabled():
    enabled = os.path.exists(password_file)
    logger.debug('get_parental_enabled: {}'.format(enabled))
    return enabled


def set_parental_enabled(setting, _password):
    logger.debug('set_parental_enabled: {}'.format(setting))

    # turning on
    if setting:
        logger.debug('enabling')

        logger.debug('setting password')
        write_file_contents(password_file, encrypt_password(_password))

        logger.debug('making the file root read-only')
        os.chmod(password_file, 0400)

        logger.debug('enabling hosts file')
        set_hosts_blacklist(True)

        msg = "Parental lock enabled!"
        logger.debug(msg)

        return True, msg

    # turning off
    else:
        # password matches
        if read_file_contents(password_file) == encrypt_password(_password):
            logger.debug('password accepted, disabling')

            logger.debug('clearing password')
            os.remove(password_file)

            logger.debug('disabling hosts file')
            set_hosts_blacklist(False)

            msg = "Parental lock disabled!"
            logger.debug(msg)

            return True, msg

        # password doesn't match
        else:
            msg = "Password doesn't match\nleaving parental lock enabled!"
            logger.debug(msg)

            return False, msg


def encrypt_password(str):
    return hashlib.sha1(str).hexdigest()


def authenticate_parental_password(passwd):
    return read_file_contents(password_file) == encrypt_password(passwd)


def create_empty_hosts():
    import platform
    hostname = platform.node()
    new_hosts = '127.0.0.1   localhost\n127.0.1.1   {}\n'.format(hostname)

    logger.debug('writing new hosts file')
    write_file_contents(hosts_file, new_hosts)

    logger.debug('restoring original hosts permission')
    os.chmod(hosts_file, 0644)


def set_hosts_blacklist(enable, blacklist_file='/usr/share/kano-settings/media/Parental/parental-hosts-blacklist.gz',
        blocked_sites=None, allowed_sites=None):
    logger.debug('set_hosts_blacklist: {}'.format(enable))

    hosts_file_backup = '/etc/kano-hosts-parental-backup'

    if not os.path.exists(hosts_file):
        create_empty_hosts()

    if enable:
        logger.debug('enabling blacklist')

        # sanity check: this is a big file, looks like the blacklist is already in place
        if os.path.getsize(hosts_file) > 10000:
            logger.debug('skipping, hosts file is already too big')
        else:
            logger.debug('making a backup of the original hosts file')
            shutil.copyfile(hosts_file, hosts_file_backup)

            logger.debug('appending the blacklist`')
            os.system('zcat %s >> %s' % (blacklist_file, hosts_file))

            logger.debug('making the file root read-only')
            os.chmod(hosts_file, 0644)

        logger.debug('Removing allowed websites')
        if allowed_sites:
            for site in allowed_sites:
                os.system('sed -i /{}/d {}'.format(site, hosts_file))

        logger.debug('Adding user-specified blacklist websites')
        if blocked_sites:
            for site in blocked_sites:
                blocked_str = ('127.0.0.1    www.{site}\n'
                               '127.0.0.1    {site}'.format(site=site))

                os.system('grep -q -F "{str}" {file} || echo "{str}" >> {file}'
                          .format(str=blocked_str, file=hosts_file))

    else:
        logger.debug('disabling blacklist')

        if os.path.exists(hosts_file_backup):
            logger.debug('restoring original backup file')
            shutil.copy(hosts_file_backup, hosts_file)

        else:
            logger.debug('cannot restore original backup file, creating new file')
            create_empty_hosts()


# Ultimate parental lock functions
####################################################

def set_ultimate_parental(enable):
    if enable:
        clear_dns_interfaces()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        whitelist = os.path.join(current_dir, '../data/WHITELIST')

        parse_whitelist_to_config_file(whitelist, sentry_config)
        redirect_traffic_to_localhost()
        launch_sentry_server(sentry_config)

    else:
        google_servers = [
            '8.8.8.8',
            '8.8.4.4'
        ]
        restore_dns_interfaces()
        set_dns(google_servers)
        refresh_resolvconf()
        kill_server()


def parse_whitelist_to_config_file(whitelist, config):
    f = open(whitelist, 'r')

    new_config = (
        '{\n'
        '    \"port\": 53,\n'
        '    \"host\": \"127.0.0.1\",\n'
        '    \"rules\": [\n'
    )
    for line in f:
        # Add line to whitelist if is non empty and doesn't start with a #
        line = line.strip()
        if line and not line.startswith('#'):
            allowed_url = (
                "        \"resolve ^(.*){} using 8.8.8.8\",\n".format(line)
            )
            new_config += allowed_url

    f.close()

    block_everything_else = (
        "        \"block ^(.*)\"\n"
        '    ]\n'
        '}'
    )
    new_config += block_everything_else

    g = open(config, 'w+')
    g.write(new_config)
    g.close()


def redirect_traffic_to_localhost():
    set_dns(['127.0.0.1'])
    refresh_resolvconf()


def launch_sentry_server(filename):
    subprocess.Popen(["sentry -c {}".format(filename)], shell=True)


def kill_server():
    # Search for "sentry -c /home/$USERNAME/.kano-settings/CONFIG"
    # in "ps aux | grep -r sentry" output
    ps_cmd = ["ps", "-A"]
    search_string = "sentry"

    ps_process = subprocess.Popen(ps_cmd, stdout=subprocess.PIPE)
    output, err = ps_process.communicate()
    lines = output.split('\n')

    # Could be very intensive
    for line in lines:
        # If the line contains the output we're looking for (i.e. is running
        # the process we're interested in)
        if search_string in line:
            pid = int(filter(None, line.split(" "))[0])
            os.kill(pid, signal.SIGKILL)
            break

####################################################


def set_chromium_policies(policies):
    if not os.path.exists(chromium_policy_file):
        ensure_dir(os.path.dirname(chromium_policy_file))
        policy_config = {}
    else:
        policy_config = read_json(chromium_policy_file)

    for policy in policies:
        policy_config[policy[0]] = policy[1]

    write_json(chromium_policy_file, policy_config)


def set_chromium_parental(enabled):
    # Policy keys and values can be found at:
    #     www.chromium.org/administrators/policy-list-3
    policies = {
        # Chromium_setting: (disabled_value, enabled_value),
        'IncognitoModeAvailability': (0, 1)
    }

    new_policy = [(key, policies[key][enabled]) for key in policies]
    set_chromium_policies(new_policy)


def set_dns_parental(enabled):
    open_dns_servers = [
        '208.67.222.123',
        '208.67.220.123'
    ]

    google_servers = [
        '8.8.8.8',
        '8.8.4.4'
    ]

    if enabled:
        logger.debug('Enabling parental DNS servers (OpenDNS servers)')
        set_dns(open_dns_servers)
        clear_dns_interfaces()
    else:
        logger.debug('Disabling parental DNS servers (Google servers)')
        set_dns(google_servers)
        restore_dns_interfaces()

    refresh_resolvconf()


def read_listed_sites():
    return (
        read_file_contents_as_lines(blacklist_file),
        read_file_contents_as_lines(whitelist_file)
    )


def write_whitelisted_sites(whitelist):
    write_file_contents(whitelist_file, '\n'.join(whitelist))


def write_blacklisted_sites(blacklist):
    write_file_contents(blacklist_file, '\n'.join(blacklist))


def set_parental_level(level_setting):
    feature_levels = [
        # Low
        ['blacklist'],
        # Medium
        ['dns'],
        # High
        ['chromium'],
        # Ultimate
        ['ultimate']
    ]

    enabled = []

    for level, features in enumerate(feature_levels):
        if level <= level_setting:
            enabled = enabled + features

    logger.debug('Setting parental control to level {}'.format(level_setting))

    if 'ultimate' in enabled:
        set_ultimate_parental('ultimate' in enabled)
    else:
        set_chromium_parental('chromium' in enabled)
        set_dns_parental('dns' in enabled)
        set_ultimate_parental(False)

    blacklist, whitelist = read_listed_sites()
    set_hosts_blacklist('blacklist' in enabled,
                        blocked_sites=blacklist, allowed_sites=whitelist)
