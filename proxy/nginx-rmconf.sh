#!/bin/sh

if test $# -ne 1
then
    cat <<EOF
Usage:
    nginx-genconf.sh NAME
EOF
exit 1
fi

name="$1"
path_enabled="/etc/nginx/sites-enabled/ngw-instance-${name}.conf"

rm "$path_enabled"
