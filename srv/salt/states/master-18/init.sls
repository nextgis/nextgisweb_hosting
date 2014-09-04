/root/lxc-genconf.sh:
    file.managed:
        - source: salt://master-18/lxc-genconf.sh
        - mode: 755

/root/lxc-rmconf.sh:
    file.managed:
        - source: salt://master-18/lxc-rmconf.sh
        - mode: 755

/usr/bin/lxc-genconf.sh:
    file.symlink:
        - target: /root/lxc-genconf.sh

/usr/bin/lxc-rmconf.sh:
    file.symlink:
        - target: /root/lxc-rmconf.sh

/etc/init/lxc.conf:
    file.managed:
        - source: salt://master-18/lxc.conf

/etc/init/lxc-net.conf:
    file.managed:
        - source: salt://master-18/lxc-net.conf

/etc/init/lxc-mounts.conf:
    file.managed:
        - source: salt://master-18/lxc-mounts.conf

/etc/init/lxc-instance.conf:
    file.managed:
        - source: salt://master-18/lxc-instance.conf
