#!/bin/sh

brctl addif lxcbr0 tap0
ip link set tap0 up
