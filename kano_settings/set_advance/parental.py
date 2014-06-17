import os
import shutil
from kano.logging import logger

password = ""


def get_parental_enabled():
    enabled = password != ""
    logger.debug('get_parental_enabled: {}'.format(enabled))
    return enabled


def set_parental_enabled(setting, _password):
    global password

    logger.debug('set_parental_enabled: {}'.format(setting))

    # turning on
    if setting:
        logger.debug('setting password')
        password = _password

        logger.debug('enabling hosts file')
        set_hosts_blacklist(True)

        msg = "Parental lock enabled!"
        logger.debug(msg)

        return True, msg

    # turning off
    else:
        # password matches
        if password == _password:
            logger.debug('clearing password')
            password = ""

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


def set_hosts_blacklist(enable, blacklist_file='/usr/share/kano-settings/media/Parental/parental-hosts-blacklist.gz'):
    logger.debug('set_hosts_blacklist: {}'.format(enable))

    blacklisted = False
    hosts_file = '/etc/hosts'
    hosts_file_backup = '/etc/kano-hosts-parental-backup'
    bare_hosts = ['127.0.0.1 kano', '127.0.0.1 localhost']

    if enable:
        # Populate a list of hosts which should not be reached (Parental browser protection)
        if os.stat(hosts_file).st_size > 1024 * 10:
            # sanity check: this is a big file, looks like the blacklist is already in place!
            pass
        else:
            # make a copy of hosts file and APPEND it with a list of blacklisted internet hostnames.
            # tighten security to the file so regular users can't peek at these host names.
            shutil.copyfile(hosts_file, hosts_file_backup)
            os.system('zcat %s >> %s' % (blacklist_file, hosts_file))
            os.system('chmod 400 %s' % (hosts_file))
            blacklisted = True
    else:
        # Restore the original list of hosts
        try:
            os.stat(hosts_file_backup)
            shutil.copy(hosts_file_backup, hosts_file)
        except:
            # the backup is gone, recreate it simply by the bare minimum needed
            with open(hosts_file, 'wt') as hhh:
                for host in bare_hosts:
                    hhh.write(host + '\n\r')

    return blacklisted
