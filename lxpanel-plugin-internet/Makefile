# Makefile
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

CC=gcc
CFLAGS=`pkg-config --cflags lxpanel gtk+-2.0`
LIBS=`pkg-config --libs lxpanel gtk+-2.0` -lkdesk-hourglass
SRC=kano_internet.c
BIN=kano_internet.so
INSTALL_PATH=/usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/lxpanel/plugins/

build: $(BIN)

install:
	install -p -m 0644 $(BIN) $(INSTALL_PATH)

$(BIN): $(SRC)
	$(CC) -Wall $(CFLAGS) -shared -fPIC $(SRC) -o $(BIN) $(LIBS)

