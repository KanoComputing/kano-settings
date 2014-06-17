import os
import shutil
import hashlib

from kano.utils import read_file_contents, write_file_contents
from kano.logging import logger

password_file = "/etc/kano-parental-lock"


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


def set_hosts_blacklist(enable, blacklist_file='/usr/share/kano-settings/media/Parental/parental-hosts-blacklist.gz'):
    logger.debug('set_hosts_blacklist: {}'.format(enable))

    hosts_file = '/etc/hosts'
    hosts_file_backup = '/etc/kano-hosts-parental-backup'

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
            os.chmod(hosts_file, 0400)

    else:
        logger.debug('disabling blacklist')

        if os.path.exists(hosts_file_backup):
            logger.debug('restoring original backup file')
            shutil.copy(hosts_file_backup, hosts_file)

        else:
            logger.debug('cannot restore original backup file, creating new file')

            import platform
            hostname = platform.node()
            new_hosts = '127.0.0.1   localhost\n127.0.1.1   {}\n'.format(hostname)

            logger.debug('writing new hosts file')
            write_file_contents(hosts_file, new_hosts)

            logger.debug('restoring original hosts permission to 644s')
            os.chmod(hosts_file, 0644)



