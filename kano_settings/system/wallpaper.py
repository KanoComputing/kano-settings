#!/usr/bin/env python

# wallpaper.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Backend wallpaper functions
#


from kano.logging import logger
import os

KDESKRC_HOME = "/home/{user}/.kdeskrc"


def change_wallpaper(path, name):
    logger.info('set_wallpaper / change_wallpaper image_name:{}'.format(name))

    # home directory
    user = os.environ['SUDO_USER']
    deskrc_path = KDESKRC_HOME.format(user=user)

    wallpapers = [
        ('medium', os.path.join(path, "{}-1024.png".format(name))),
        ('4-3', os.path.join(path, "{}-4-3.png".format(name))),
        ('16-9', os.path.join(path, "{}-16-9.png".format(name)))
    ]
    conf_param_template = 'Background.File-{size}'
    conf_params = dict()

    for size, image in wallpapers:
        conf_param = conf_param_template.format(size=size)
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
