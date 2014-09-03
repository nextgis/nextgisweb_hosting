#!/bin/sh

if test $# -ne 1
then
    cat <<EOF
Usage:
    nginx-rmconf.sh ID
EOF
exit 1
fi

id="$1"
path_available="/etc/nginx/sites-available/ngw-${id}.conf"
path_enabled="/etc/nginx/sites-enabled/ngw-${id}.conf"

rm "$path_enabled"
rm "$path_available"

