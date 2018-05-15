# Networking in Kanux
## Introduction

KanuxOS system is network ready from first boot, with ipv4 support. This document explains the various options.

Kanux supports the following connectivity devices:

- Ethernet
- WiFi
- Android USB

### Ethernet

Ethernet connectivity should always be ready functioning. Simply plug the network cable to a dhcp-ready network and Kanux will acquire a DHCP lease automatically.

### USB devices

In order to enable the network interface for the USB port to work with tethering you need to do the following: Edit the following file as root `sudo vi /etc/network/interfaces` and add the line `iface usb0 inet dhcp` in the end of the file, which enables the `dhcp` service for the USB port.

After this run `sudo ifup usb0` and reboot. Now enable tethering on your mobile device, just connect it to the Kanux and you should be online!

### WiFi

Raspbian `Jessie` is not following the usual `Debian` approach to networking with`/etc/network/if-*` scripts. Instead `dhcpcd` is used. `dhcpcd` is an implementation of the `DHCP` client specified in `RFC 2131`. It gets the host information (`IP`address, routes, etc) from a `DHCP` server and configures the network interface of the machine on which it is running.

It then runs the configuration script which writes `DNS` information to `resolvconf`, if available, otherwise directly to `/etc/resolv.conf`. If the `hostname` is currently `blank`, (`null`) or `localhost`, or `force_hostname` is `YES` or `TRUE` or `1` then dhcpcd sets the hostname to the one supplied by the `DHCP` server.

`dhcpcd` then daemonises and waits for the lease renewal time to lapse. It will attempt to renew its lease and reconfigure if the new lease changes, when the lease begins to expire, or the `DHCP` server sends message to renew early.

It turns out that `dhcpcd` has a very neat way of hooking up into the network configuration: all you need to do is drop a script in the `/lib/dhcpcd/dhcpcd-hooks` directory, and it will get called at the various stages of the IP allocation process. The script will receive a bunch of useful variables like `${interface}` and `${new_ip_address}` that make it easy to get all the data we need. Check also the `dhcpcd-run-hooks` man page!

#### Graphical

If you need to connect to other wireless networks, open the "Wifi" app icon on the right hand end of the menu bar, or execute "sudo kano-wifi" from the command line. Once you successfully connect to a wireless network, it will be remembered, so next time you boot Kanux it will automatically connect to the network if it is in range.

#### Command Line

In case you need to fine tune more specific wireless secured networks, kano-wifi allows you to provide a custom wpa_supplicant configuration file, like this:

`sudo kano-wifi /path/to/my/wpa_supplicant.conf`

Make sure you provide an absolute path filename to avoid problems during automatic connect at boot time. As an example here's a small simple file to connect to a WPA2 network:

```bash
network={
    ssid="myssid"
    scan_ssid=1
    proto=WPA RSN
  	key_mgmt=WPA-PSK
  	pairwise=CCMP TKIP
  	group=CCMP TKIP
  	psk="mypassword"
}

network={
    ssid="myschoolssid"
    psk="schoolpassword"
    id_str="school"
}
```

The wpa supplicant daemon log file is saved under /var/log/kano_wpa.log where you can find inner details on the association sequence.

If you need to configure the password as a 32 byte hexadecimal number you can use the tool `wpa_passphrase "myssid" "mypassword"`to generate it. As shown in the example, two different networks can be used (for example one for home and one for a school `ssid`.)

Note: As the hook scripts are initiated by a common bash process, the variables in them are passed through without the need of using an environment variable or sourcing the scripts onto each one.

### IPv6 support

The kernel has built-in support for IPv6 networking but is disabled by default. To enable it, either `sudo modprobe ipv6` or add `ipv6` in the file `/etc/modules` and restart the system:

- [Raspbian FAQ](http://www.raspbian.org/RaspbianFAQ#How_do_I_enable_or_use_IPv6.3F)

More in-depth information regarding IPv6 and its use in Debian can be found here:

- [Debian IPv6](https://wiki.debian.org/DebianIPv6)

### WPA supplicant

The way that the default `wpa supplicant` (v2.4) but also (testing v2.6 `sid` for `armhf`) ships with the new Raspbian based Stretch (Debian 9/May 2018) creates issues in the WiFi connection. A solution to this was employed by compiling a custom `wpa supplicant` based on the latest (v2.6) source and the following configuration:

```bash
cat > wpa_supplicant/.config << "EOF"
CONFIG_BACKEND=file
CONFIG_CTRL_IFACE=y
CONFIG_DEBUG_FILE=y
CONFIG_DEBUG_SYSLOG=y
CONFIG_DEBUG_SYSLOG_FACILITY=LOG_DAEMON
CONFIG_DRIVER_NL80211=y
CONFIG_DRIVER_WEXT=y
CONFIG_DRIVER_WIRED=y
CONFIG_EAP_GTC=y
CONFIG_EAP_LEAP=y
CONFIG_EAP_MD5=y
CONFIG_EAP_MSCHAPV2=y
CONFIG_EAP_OTP=y
CONFIG_EAP_PEAP=y
CONFIG_EAP_TLS=y
CONFIG_EAP_TTLS=y
CONFIG_IEEE8021X_EAPOL=y
CONFIG_IPV6=y
CONFIG_LIBNL32=y
CONFIG_PEERKEY=y
CONFIG_PKCS12=y
CONFIG_READLINE=y
CONFIG_SMARTCARD=y
CONFIG_WPS=y
CFLAGS += -I/usr/include/libnl3
CONFIG_CTRL_IFACE_DBUS=y
CONFIG_CTRL_IFACE_DBUS_NEW=y
CONFIG_CTRL_IFACE_DBUS_INTRO=y
EOF

```

It is important that `P2P` isn't defined as supported otherwise it creates a virtual `wlan0` interface that conflicts with our approach to WiFi connection.

A few libraries needed to sucessfully build the `wpa supplicant` including:

```bash
sudo apt-get install build-essential libnl-3-dev libnl-genl-3-dev libdbus-1-dev gobject-introspection libgirepository1.0-dev libclutter-1.0-dev
```

After a sucessfull compilation a custom `deb`ian package needs to be created. Additionaly two new configuration files "/etc/network/interfaces" as simple as in the following.

```bash
auto lo
iface lo inet loopback
```
and `/etc/wpa_supplicant/wpa_supplicant.conf`

```bash
ctrl_interface=/run/wpa_supplicant
update_config=1
```
