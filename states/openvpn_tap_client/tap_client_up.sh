#!/bin/sh

ip link set tap0 up
(
  sleep 5
  dhclient tap0
  ip route add 192.168.19.0/24 via 192.168.18.1
  resolvconf -u
) &

