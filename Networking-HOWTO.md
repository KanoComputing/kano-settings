## Kanux networking HowTo

KanuxOS system is network ready from first boot, with ipv4 support.
This document explains the various options you have to network the system
to the outside world.

Kanux supports at least the following connectivity devices:

- Ethernet
- Kano Wireless wifi dongle 
- Android  USB 

### Ethernet

Ethernet connectivity should always be ready functioning. Simply plug the network cable
to a dhcp-ready network and Kanux will acquire a DHCP lease automatically.

### USB devices

Kanux should also play nice with Android and iPhone USB tethering devices.
Simply plug the usb cable, enable tethering, and Kanux will acquire a DHCP lease automatically.

### Wireless

Wireless is enabled out of the box, and as soon as you plug Kano usb wifi dongle.
At bootup, if a wireless network is in range with ssid "kanux"
WPA-PSK encryption enabled with passphrase "kanuxpass", it will
be connected to automatically. 

You can setup your wireless router, or you can also put your mobile device
in "Wireless tethering" mode. Note that Kanux fully supports the wireless dongle
provided. Other wifi dongles should work as well but have not been fully tested.

If you need to connect to other wireless networks, open the "Wifi" app icon
in the Extras folder, or execute "sudo kano-wifi" from the command line.

Once you successfully connect to a wireless network, it will be remembered,
so next time you boot Kanux it will automatically connect to the network
if it is in range.

IMPORTANT: Please note that plugging the wireless dongle while the RaspberryPI
is functioning will almost certainly cause a hardware reset. This is a
hardware limitation on the RaspberryPI device itself present as of the time
of this writing.

### IPv6 support

The kernel has built-in support for IPv6 networking but is disabled by default.
To enable it, either "modprobe ipv6" or add "ipv6" in the file /etc/modules
and restart the system:

- http://www.raspbian.org/RaspbianFAQ#How_do_I_enable_or_use_IPv6.3F

More in-depth information regarding ipv6 can be found here:

- https://wiki.debian.org/DebianIPv6
