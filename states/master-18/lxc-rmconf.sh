#!/bin/sh

lvname="$1" 
lvgroup="ngw"

lxc-stop --name ${lvgroup}-${lvname}
initctl stop lxc-mounts lvname=${lvname} lvgroup=${lvgroup}
rm ~virtualizer/lxc/${lvgroup}-${lvname}/config
rmdir ~virtualizer/lxc/${lvgroup}-${lvname}/rootfs
rmdir ~virtualizer/lxc/${lvgroup}-${lvname}
tar -cf ~virtualizer/data.d/${lvgroup}-${lvname}.tar ~virtualizer/data.d/${lvgroup}-${lvname}
rm -rf ~virtualizer/data.d/${lvgroup}-${lvname}
lvremove --force ${lvgroup}/${lvname}

