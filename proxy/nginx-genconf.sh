#!/bin/sh

if test $# -ne 3
then
    cat <<EOF
Usage:
    nginx-genconf.sh NAME FQDN_FRONTEND FQDN_BACKEND
EOF
exit 1
fi

name="$1"
fqdn_frontend="$2"
fqdn_backend="$3"

path="/etc/nginx/sites-available/ngw-instance-${name}.conf"
path_enabled="/etc/nginx/sites-enabled/ngw-instance-${name}.conf"

cat > "$path" <<EOF

server {

    listen 80;
    server_name ${fqdn_frontend};

    location / {

        # Since I utilize dynamic (DHCP) IP address allocation for the backend cluster,
        # I should provision for changing backend IP address. And that's how.
        resolver 192.168.17.6;
        resolver_timeout 10s;

        set \$backend_upstream_wsgi "${fqdn_backend}:9090";


        include uwsgi_params;
        uwsgi_pass \$backend_upstream_wsgi;
    }
}

EOF

ln -sf \
    "$path" \
    "$path_enabled" 
