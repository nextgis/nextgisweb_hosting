#!/bin/sh

if test $# -ne 2
then
    cat <<EOF
USAGE:
    call-create.sh NAME IMAGE
EOF
    exit 1
fi


name="$1"
image="$2"

# salt-call event.fire_master         \
#     "{ 'host': 'salt.ngw' , 'database': '${name}_d' , 'username': '${name}_u' , 'password': '${name}_p' , 'identifier': '${name}' , 'image': '${image}' , 'hostname': '${name}' } "                               \
#     "ngw/create"

salt-call event.fire_master \
    "{ 'id': '${name}' , 'class': '${image}' , 'name': '${name}' } " \
    "ngw/create"
