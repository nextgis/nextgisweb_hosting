#!/bin/sh

f_create () {
    id="$1"
    class="$2"
    name="$1"

    salt-call event.fire_master \
        "{ 'id': '${id}' , 'class': '${class}' , 'name': '${name}' } " \
        "ngw/create"
}

f_destroy () {
    id="$1"

    salt-call event.fire_master \
        "{ 'id': '${id}' } " \
        "ngw/destroy"
}

if test $# -eq 0
then
    cat <<EOF
USAGE:
    ngw-manager.sh ACTION ARGS
EOF
    exit 1
fi

action="$1"
shift

case $action in

    (create)
        f_create "$@"
        logger -p local0.notice -t NGW-MANAGE \
            "Manager was called for a valid event <$action> with $# arguments."
        ;;

    (destroy)
        f_destroy "$@"
        ;;

    (*)
        logger -p local0.error -t NGW-MANAGE \
            "Manager was called for an unknown kind of event: <$action>"
        exit 1
        ;;

esac

exit 0
