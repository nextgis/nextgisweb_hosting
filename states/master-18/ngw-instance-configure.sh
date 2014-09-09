#!/bin/sh

if test $# -ne 4
then
    cat << EOF
USAGE:
    ngw-instance-config.sh IDENTIFIER DATABASE USERNAME PASSWORD
EOF
    exit 1
fi

instance="$1"
config="/var/lib/lxc/ngw-${instance}/rootfs/home/ngw/config.ini"
timestamp=$(date +%s)

database="$2"
username="$3"
password="$4"

if ! test -f "$config"
then
    echo "Instance unexistent!"
    exit 1
fi

if
    cp "$config" "$config".$timestamp.archive
then 
    cat > "$config" << EOF

[core]

system.name = NextGIS Web
system.full_name = NextGIS Web
database.host = db-precise.ngw
database.name = ${database:?}
database.user = ${username:?}
database.password = ${password:?}
# database.check_at_startup =
# packages.ignore =
# components.ignore =

[pyramid]

secret = nextgis

[feature_layer]

# identify.attributes =

[file_upload]

path = /tmp

[file_storage]

path = /data

[webmap]

# basemaps =
# bing_apikey =
# identify_radius =
# popup_width =
# popup_height =

[wmsclient]


[mapserver]

# fontset =

EOF
    if test "$(md5sum "$config")" = "$(md5sum "$config".$timestamp.archive)"
    then
        rm "$config".$timestamp.archive
    fi
fi

