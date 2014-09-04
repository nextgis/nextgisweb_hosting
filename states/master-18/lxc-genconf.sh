#!/bin/sh

logfile="/var/log/ngw/gen.log"

log () { 
    echo $(date) / $(basename $0): "$@" >> $logfile
}


if test $# -ne 2
then
    cat <<EOF
USAGE:
    lxc-genconf.sh LVNAME LVIMAGE 
EOF
exit 1
fi

lvname="$1" 
lvgroup="ngw"
path="/var/lib/lxc/${lvgroup}-${lvname}"
lvimage="$2"

lvcreate --type thin --name ${lvname} --snapshot ${lvimage} --thinpool ${lvgroup}/pool0
lvchange -ay -kn ${lvgroup}/${lvname}
initctl start lxc-mounts lvname=${lvname} lvgroup=${lvgroup}

# This is kinda naive precaution.
# Example: domain-my.host_name turns to my-host-name.domain.
host=$( echo "${lvname}" | tr '._' '--' ).${lvgroup}

if ! [ -d "$path" ]
then
    echo "No such container!" > /dev/stderr
    exit 1
fi

if [ -f "$path"/config ]
then
    echo "File exists!" > /dev/stderr
    exit 1
fi

cat > "$path"/config <<EOF

lxc.utsname = "$host"
lxc.rootfs = /var/lib/lxc/${lvgroup}-${lvname}/rootfs                                              
lxc.start.auto = 1 

lxc.network.type = veth                                                                               
lxc.network.link = lxcbr0

lxc.mount.entry = sysfs sys sysfs defaults 0 0                                                        
lxc.mount.entry = /sys/fs/fuse/connections sys/fs/fuse/connections none bind,optional 0 0             
lxc.mount.entry = /sys/kernel/debug sys/kernel/debug none bind,optional 0 0                           
lxc.mount.entry = /sys/kernel/security sys/kernel/security none bind,optional 0 0                     
lxc.mount.entry = /sys/fs/pstore sys/fs/pstore none bind,optional 0 0                                 

lxc.tty = 4                                                                                           
lxc.pts = 1024                                                                                        
lxc.devttydir = lxc                                                                                   
lxc.arch = x86_64                                                                                     

lxc.cgroup.devices.deny = a                                                                           
lxc.cgroup.devices.allow = c *:* m                                                                    
lxc.cgroup.devices.allow = b *:* m                                                                    
lxc.cgroup.devices.allow = c 1:3 rwm                                                                  
lxc.cgroup.devices.allow = c 1:5 rwm                                                                  
lxc.cgroup.devices.allow = c 5:0 rwm                                                                  
lxc.cgroup.devices.allow = c 5:1 rwm                                                                  
lxc.cgroup.devices.allow = c 1:8 rwm                                                                  
lxc.cgroup.devices.allow = c 1:9 rwm                                                                  
lxc.cgroup.devices.allow = c 5:2 rwm                                                                  
lxc.cgroup.devices.allow = c 136:* rwm                                                                
lxc.cgroup.devices.allow = c 254:0 rm                                                                 
lxc.cgroup.devices.allow = c 10:229 rwm                                                               
lxc.cgroup.devices.allow = c 10:200 rwm                                                               
lxc.cgroup.devices.allow = c 1:7 rwm                                                                  
lxc.cgroup.devices.allow = c 10:228 rwm                                                               
lxc.cgroup.devices.allow = c 10:232 rwm                                                               

lxc.cap.drop = sys_module                                                                             
lxc.cap.drop = mac_admin                                                                              
lxc.cap.drop = mac_override                                                                           
lxc.cap.drop = sys_time                                                                               

lxc.pivotdir = lxc_putold                                                                             

EOF

echo "$host" > "$path"/rootfs/etc/hostname

if [ -e "$path"/rootfs/etc/salt/minion_id ]
then
    echo -n "$host" > "$path"/rootfs/etc/salt/minion_id
fi

# lxc-start --daemon --name ${lvgroup}-${lvname}

exit 0

