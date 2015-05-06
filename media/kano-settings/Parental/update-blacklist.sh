#!/bin/sh

HOSTFILE_URL=http://www.hostsfile.org/Downloads/BadHosts.unx.zip
HOSTS_DIR=BadHosts.unx
HOSTS_ZIP=$HOSTS_DIR.zip
BLACKLIST_FILE=parental-hosts-blacklist

curl $HOSTFILE_URL > $HOSTS_ZIP
unzip $HOSTS_ZIP

cat $HOSTS_DIR/add.Casino > $BLACKLIST_FILE
cat $HOSTS_DIR/add.Porn >> $BLACKLIST_FILE
cat $HOSTS_DIR/add.Risk >> $BLACKLIST_FILE

# Append the kano list
cat kano-blacklist >> $BLACKLIST_FILE

gzip -f $BLACKLIST_FILE

# Clean up
rm -rf $HOSTS_DIR
rm -f $HOSTS_ZIP
