#!/usr/bin/env python

# wallpaper.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Backend wallpaper functions
#


from kano.logging import logger
from kano.utils import get_user_unsudoed
import os

KDESKRC_SYSTEM = "/usr/share/kano-desktop/kdesk/.kdeskrc"
KDESKRC_HOME_TEMPLATE = "/home/{user}/.kdeskrc"

PARAM_NAME_TEMPLATE = "Background.File-{size}"
SIZE_SUFFIX_MAP = {
    "medium": "-1024.png",
    "4-3": "-4-3.png",
    "16-9": "-16-9.png"
}


def _get_wallpaper_from_kdeskrc(kdeskrc_path):
    """
        Parses a .kdeskrc file and looks for wallpaper configuration keys.

        :param kdeskrc_path: Location of the file to be parsed.
        :type kdeskrc_path: str

        :return: A map of wallpaper types to file paths.
        :rtype: dict
    """

    wallpapers = {}

    if not os.path.isfile(kdeskrc_path):
        return wallpapers

    with open(kdeskrc_path, 'r') as kdesk_conf:
        for kdesk_conf_line in kdesk_conf:
            for key, suffix in SIZE_SUFFIX_MAP.iteritems():
                conf_param = PARAM_NAME_TEMPLATE.format(size=key)
                token = "{}:".format(conf_param)
                if token in kdesk_conf_line:
                    path = kdesk_conf_line.split(token)[-1].strip()
                    wallpapers[key] = path

    return wallpapers


def get_current_wallpapers():
    """
        Returns the current wallpaper configuration.

        :return: A map of wallpaper types to file paths.
        :rtype: dict
    """

    wallpapers = {key: None for key in SIZE_SUFFIX_MAP.iterkeys()}
    wallpapers.update(_get_wallpaper_from_kdeskrc(KDESKRC_SYSTEM))

    home_dir = KDESKRC_HOME_TEMPLATE.format(user=get_user_unsudoed())
    wallpapers.update(_get_wallpaper_from_kdeskrc(home_dir))

    return wallpapers


def change_wallpaper(path, name):
    logger.info('set_wallpaper / change_wallpaper image_name:{}'.format(name))

    # home directory
    user = get_user_unsudoed()
    deskrc_path = KDESKRC_HOME_TEMPLATE.format(user=user)

    conf_params = {}
    for size, suffix in SIZE_SUFFIX_MAP.iteritems():
        conf_param = PARAM_NAME_TEMPLATE.format(size=size)
        image = os.path.join(path, "{}{}".format(name, suffix))
        conf_params[conf_param] = "  {param}: {image}".format(param=conf_param,
                                                              image=image)

    found = False
    newlines = []

    if os.path.isfile(deskrc_path):
        with open(deskrc_path, 'r') as kdesk_conf:
            for kdesk_conf_line in kdesk_conf:
                for conf_param, conf_line in conf_params.iteritems():
                    if conf_param in kdesk_conf_line:
                        kdesk_conf_line = conf_line
                        found = True

                newlines.append(kdesk_conf_line + '\n')

    if found:
        # Overwrite config file with new lines
        with open(deskrc_path, 'w') as outfile:
            outfile.writelines(newlines)
    else:
        # Not found so add it
        with open(deskrc_path, "a") as outfile:
            for conf_line in conf_params.itervalues():
                outfile.write(conf_line + '\n')

    # Refresh the wallpaper
    os.system('sudo -u {user} kdesk -w'.format(user=user))

    return 0


# Module debug
if __name__ == '__main__':
    print get_current_wallpapers()
