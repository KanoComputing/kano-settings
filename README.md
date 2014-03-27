# kano-settings


Graphic tool to setup Kanux: email, keyboard, audio, display, wifi...

## kano-connect

This script attempts to find an open wireless network and connect to it.
Additionally it is capable of reconnecting to secure networks associated to by
kwifiprompt.

Usage:
- Case 1: Attempt connection to the strongest wireless non-secure network
$ sudo kanoconnect.py wlan0

- Case 2: Attempt connection to a specified open network
$ sudo kanoconnect.py wlan0 essidname

- Case 3: If the last cached network is found during scan, try to connect to
  it (secure / unsecure)
$ sudo kanoconnect.py -c wlan0

It might take some time for this script to finalise, depending on the wireless
networks in range, their signal strenght and response times to acquire a DHCP
lease.

Portions of this code are extracted from the project pywilist:
https://code.google.com/p/pywilist/

The script needs root permissions. It is good to trigger it from
`/etc/network/interfaces` post-up event.

## kano-wifi

This script is a guided, interactive step-by-step process to connect to a
wireless network. Sets return code to 0 if connected, anything else meaning
an error occured.

Exit codes:
 - 1 need root privileges
 - 2 no wifi dongle connected
 - 3 a connection attempt is already in progress
