# Makefile
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

CC=gcc
CFLAGS=`pkg-config --cflags lxpanel gtk+-2.0` -I/usr/include/libfm
LIBS=`pkg-config --libs lxpanel gtk+-2.0` -lfm-gtk -lkdesk-hourglass
SRC=kano_settings.c
BIN=kano_settings.so
INSTALL_PATH=/usr/lib/arm-linux-gnueabihf/lxpanel/plugins/

build: $(BIN)

install:
	install -p -m 0644 $(BIN) $(INSTALL_PATH)

$(BIN): $(SRC)
	$(CC) -Wall $(CFLAGS) -shared -fPIC $(SRC) -o $(BIN) $(LIBS)

