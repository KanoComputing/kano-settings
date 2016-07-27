#!/usr/bin/env python

# boot_config.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Functions controlling reading and writing to /boot/config.txt
#
# NOTE this api has changed to use a transactional approach.
# See documentation at the start of ConfigTransaction()

import atexit
import re
import os
import sys
import shutil
import tempfile

from kano.utils.file_operations import read_file_contents_as_lines, open_locked
from kano.utils.misc import is_number
from kano.logging import logger

boot_config_standard_path = "/boot/config.txt"
BACKUP_BOOT_CONFIG_TEMPLATE = "/boot/config_{model}_backup.txt"
default_config_path = "/usr/share/kano-settings/boot_default/config.txt"

tvservice_path = '/usr/bin/tvservice'
boot_config_safemode_backup_path = '/boot/config.txt.orig'
lock_dir = '/run/lock'
noobs_line = "# NOOBS Auto-generated Settings:"

dry_run = False
lock_timeout = 5

def set_dry_run():
    """
    Set dry run on all config files.
    """
    global dry_run
    dry_run = True


class BootConfig:
    # Class which knows how to make individual modifications to a config file.
    # Should only be used within this module to allow locking.

    CONFIG_FILTER_PATTERN = r'^\[(\w*)=?([\w\-]*)\]$'
    CONFIG_FILTER_RE = re.compile(CONFIG_FILTER_PATTERN)

    def __init__(self, path=boot_config_standard_path, read_only=True):
        self.path = path
        self.read_only = read_only

    @staticmethod
    def new_from_model(model):
        model = re.sub(r'[-/ ]', '', model).lower()
        model_config_file = BACKUP_BOOT_CONFIG_TEMPLATE.format(model=model)

        return BootConfig(model_config_file)

    def exists(self):
        return os.path.exists(self.path)

    def ensure_exists(self):
        if not self.exists():
            f = open_locked(self.path, "w")
            print >>f, "#"  # otherwise set_value thinks the file should not be written to

            # make sure changes go to disk
            f.flush()
            os.fsync(f.fileno())

            f.close()  # make file, even if empty

    def _noobs_defaults_present(self):
        lines = read_file_contents_as_lines(self.path)
        return noobs_line in lines

    def _remove_noobs_defaults(self):
        """
        Remove the config entries added by Noobs,
        by removing all the lines after and including
        noobs' sentinel

        """
        lines = read_file_contents_as_lines(self.path)
        with open_locked(self.path, "w") as boot_config_file:

            for line in lines:
                if line == noobs_line:
                    break
                
                boot_config_file.write(line + "\n")
                
            # flush changes to disk
            boot_config_file.flush()
            os.fsync(boot_config_file.fileno())


    def check_corrupt(self):

        # Quick check for corrpution in config file.
        # Check that is has at least some expected data
        try:
            lines = read_file_contents_as_lines(self.path)
        except:
            return True

        must_contain = set(['overscan_bottom', 'over_voltage'])
        found = set()

        for l in lines:
            for m in must_contain:
                if m in l:
                    found.add(m)
        return must_contain != found


    @classmethod
    def get_current_filter(cls, current_filter, line):
        filter_match = cls.CONFIG_FILTER_RE.match(line)

        if not filter_match:
            return current_filter

        filter_groups = filter_match.groups()
        new_filter = filter_groups[0]

        if filter_groups[1]:
            new_filter += '=' + filter_groups[1]

        return new_filter

    @staticmethod
    def sanitise_filter(config_filter):
        pass


    def set_value(self, name, value=None, config_filter=''):
        # if the value argument is None, the option will be commented out
        lines = read_file_contents_as_lines(self.path)
        if not lines:  # this is true if the file is empty, not sure that was intended.
            return

        logger.info('writing value to {} {} {}'.format(self.path, name, value))

        option_re = r'^\s*#?\s*' + str(name) + r'=(.*)'
        current_filter = ''

        with open_locked(self.path, "w") as boot_config_file:
            was_found = False

            for line in lines:
                current_filter = self.get_current_filter(current_filter, line)

                if current_filter == config_filter \
                        and re.match(option_re, line):
                    was_found = True
                    if value is not None:
                        replace_str = str(name) + "=" + str(value)
                    else:
                        replace_str = r'#' + str(name) + r'=0'
                    new_line = replace_str
                else:
                    new_line = line

                boot_config_file.write(new_line + "\n")

            if not was_found and value is not None:
                if config_filter:
                    boot_config_file.write('[' + config_filter + ']\n')

                boot_config_file.write(str(name) + "=" + str(value) + "\n")

            # flush changes to disk
            boot_config_file.flush()
            os.fsync(boot_config_file.fileno())

    def get_value(self, name, config_filter=''):
        lines = read_file_contents_as_lines(self.path)
        if not lines:
            return 0

        current_filter = ''

        for l in lines:
            current_filter = self.get_current_filter(current_filter, l)

            if current_filter == config_filter \
                    and l.startswith(name + '='):
                value = l.split('=')[1]
                if is_number(value):
                    value = int(value)
                return value

        return 0

    def set_comment(self, name, value):
        lines = read_file_contents_as_lines(self.path)
        if not lines:
            return

        logger.info('writing comment to {} {} {}'.format(self.path, name, value))

        comment_str_full = '### {}: {}'.format(name, value)
        comment_str_name = '### {}'.format(name)

        with open_locked(self.path, "w") as boot_config_file:
            boot_config_file.write(comment_str_full + '\n')

            for line in lines:
                if comment_str_name in line:
                    continue

                boot_config_file.write(line + '\n')

            # make sure changes go to disk
            boot_config_file.flush()
            os.fsync(boot_config_file.fileno())

    def get_comment(self, name, value):
        lines = read_file_contents_as_lines(self.path)
        if not lines:
            return False

        comment_str_full = '### {}: {}'.format(name, value)
        return comment_str_full in lines

    def has_comment(self, name):
        lines = read_file_contents_as_lines(self.path)
        if not lines:
            return False

        comment_start = '### {}:'.format(name)
        for l in lines:
            if l.startswith(comment_start):
                return True

        return False


class OpenTransactionError(Exception):
    """
    Exception denoting that a transaction was left open
    """
    pass


class ConfigTransaction:
    def __init__(self, path):
        # This class represents a transaction on the config files.
        #  It ensures that only one process can execute a transaction at a time.
        #  A transaction is defined as starting when any read or write operation is
        #  performed, eg get get_config_value, and ending when either close()
        #  or abort() is called.
        #
        # To make the transaction atomic, when any write operation is called,
        # a temporary copy of config.txt is made. This is then used for all read or write
        # opertions until the transaction is ended.
        #  
        #  It has three states:
        #  * 0 : IDLE
        #  * 1 : Locked
        #  * 2 : Writable

        # The attributes 'lock' and 'temp_config'
        # and 'temp_path' have different values depending on state - 
        # see valid_state().

        # To initialise a transaction, we do two things:
        #  * Obtain a lockfile in a tempfs directory
        #    (so even if we are killed, it will not persist across boots)
        #  * make a new file with a unique name in the same directory as the
        #    config file we are going to modify
        self.path = path
        self.base = os.path.basename(path)
        self.dir = os.path.dirname(path)

        self.lockpath = os.path.join(lock_dir,
                                     'kano_config_'+self.base+'.lock')

        self.state = None
        self.set_state_idle()

    def valid_state(self):
        # validity condition for states
        if self.state == 0:
            return (self.lock is None and
                    isinstance(self.temp_config, BootConfig) and
                    self.temp_config.path == self.path and
                    self.temp_path is None
                    )
        if self.state == 1:
            return (isinstance(self.lock, open_locked) and
                    self.temp_config.path == self.path and
                    self.temp_path is None
                    )
        if self.state == 2:
            return (isinstance(self.lock, open_locked) and
                    self.temp_config.path == self.temp_path and
                    self.temp_path is not None
                    )

    def set_state_idle(self):
        if self.state is None:
            self.temp_config = BootConfig(self.path)
            self.temp_path = None
            self.lock = None
            self.state = 0

        if self.state == 2:
            # For pure read operations, set up access to config
            self.temp_config = BootConfig(self.path)
            self.state = 1
            self.temp_path = None

        if self.state == 1:
            self.lock.close()
            self.lock = None
            self.state = 0

    def raise_state_to_locked(self):
        if self.state == 0:
            self.state = 1
            self.lock = open_locked(self.lockpath, "w", timeout=lock_timeout)

    def set_state_writable(self):

        if self.state == 0:
            self.raise_state_to_locked()

        if self.state == 1:

            temp = tempfile.NamedTemporaryFile(mode="w",
                                               delete=False,
                                               prefix="config_tmp_",
                                               dir=self.dir)
            self.temp_path = temp.name
            logger.info("Enable modifications in  config transaction: {}".format(self.temp_path))
            temp.close()
            shutil.copyfile(self.path, self.temp_path)

            # create temporary
            self.temp_config = BootConfig(self.temp_path)

        self.state = 2

    def set_config_value(self, name, value=None):
        self.set_state_writable()
        self.temp_config.set_value(name, value)

    def get_config_value(self, name):
        self.raise_state_to_locked()
        return self.temp_config.get_value(name)

    def set_config_comment(self, name, value):
        self.set_state_writable()
        self.temp_config.set_comment(name, value)

    def get_config_comment(self, name, value):
        self.raise_state_to_locked()
        return self.temp_config.get_comment(name, value)

    def has_config_comment(self, name):
        self.raise_state_to_locked()
        return self.temp_config.has_comment(name)

    def remove_noobs_defaults(self):
        # NB, unlike the other methods, this may or may not require close.
        # It returns true if it does (also to trigger a reboot)
        self.raise_state_to_locked()
        present = self.temp_config._noobs_defaults_present()
        if present:
            self.set_state_writable()
        self.temp_config._remove_noobs_defaults()
        return present

    def copy_to(self, dest):
        # Copy to a file. Note that if we have modified in this transaction,
        # include the changes.

        # Note that although internal, this function is used in
        # kano-updater post-update scenario beta_310_to_beta_320
        
        self.raise_state_to_locked()
        if self.temp_path:
            path = self.temp_path
        else:
            path = self.path
        shutil.copy2(path, dest)

    def copy_from(self, src):
        # Note that although internal, this function is used in
        # kano-updater post-update scenario beta_310_to_beta_320
        
        self.set_state_writable()
        shutil.copy2(src, self.temp_path)

    def check_corrupt_config(self):
        self.raise_state_to_locked()
        if self.temp_config.check_corrupt():
            self.copy_from(default_config_path)
            return True
        return False

    def close(self):
        if self.state == 2:
            if dry_run:
                logger.info("dry run config transaction can be found in {}".format(self.temp_path))
            else:
                logger.info("closing config transaction")
                shutil.move(self.temp_path, self.path)
                # sync
                dirfd = os.open(self.dir, os.O_DIRECTORY)
                os.fsync(dirfd)
                os.close(dirfd)
                os.system('sync')

        else:
            logger.warn("closing config transaction with no edits")
        self.set_state_idle()

    def _clean_up_exit(self):
        # for program exit: check if the transaction has been left open,
        # close it, and raise an error.

        # NB, we don't complain if only reads have happened. Ideally
        # we might want to close read transactions to avoid locking for
        # long periods, but it's not a safety issue so leave it for now.

        if self.state > 1:
            self.close()
            raise OpenTransactionError()

    def abort(self):
        os.remove(self.temp_path)
        self.set_state_idle()


def enforce_pi():
    pi_detected = os.path.exists(tvservice_path) and \
        os.path.exists(boot_config_standard_path)
    if not pi_detected:
        logger.error('need to run on a Raspberry Pi')
        sys.exit()


_transaction = None

def _trans():
    # Note that although internal, this function is used in
    # kano-updater post-update scenario beta_310_to_beta_320
    global _transaction
    if not _transaction:
        _transaction = ConfigTransaction(boot_config_standard_path)
    return _transaction

def set_config_value(name, value=None, config_filter=''):
    _trans().set_config_value(name, value, config_filter)


def get_config_value(name):
    return _trans().get_config_value(name)


def set_config_comment(name, value):
    _trans().set_config_comment(name, value)


def get_config_comment(name, value):
    return _trans().get_config_comment(name, value)


def has_config_comment(name):
    return _trans().has_config_comment(name)


def remove_noobs_defaults():
    return _trans().remove_noobs_defaults()


def end_config_transaction():
    _trans().close()


def end_config_transaction_no_writeback():
    _trans().abort()


def is_safe_boot():
    """ Test whether the unit is booting in the safe mode already. """

    return os.path.isfile(boot_config_safemode_backup_path)


def safe_mode_backup_config():
    _trans().copy_to(boot_config_safemode_backup_path)


def safe_mode_restore_config():
    _trans().copy_from(boot_config_safemode_backup_path)
    # remove backup file to indicate we are not in safe mode any more
    os.unlink(boot_config_safemode_backup_path)


def check_corrupt_config():
    return _trans().check_corrupt_config()


# Register handler to make sure transaction is closed.

def _clean_up_exit():
    _trans()._clean_up_exit()

atexit.register(_clean_up_exit)
