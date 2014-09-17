#!/bin/sh

# set -x
# 
# exec >>/tmp/`basename $0`.out 2>>/tmp/`basename $0`.err

f_event () {
    # I notice salt event system loses events too often. Hence this.
    
    SLEEP=2
    RETRIES=1

    event_message="$1"
    event_tag="$2"
            logger -p local0.notice -t NGW-MANAGE \
                "Entering function <$id>! "

    export PGHOST=db-precise
    export PGDATABASE=front
    export PGUSER=front
    export PGPASSWORD=front 

    psql -At -c " update \"instances\" set \"instanceeventaccepted\" = False where \"instanceid\" = '$id' ; " 

            logger -p local0.notice -t NGW-MANAGE \
                "updated with false"

    flag=''
    i=0
    while [ "x$flag" = 'x' ]
    do
        salt-call event.fire_master "$event_message" "$event_tag" 
        logger -p local0.notice -t NGW-MANAGE \
            "Event sent, waiting for confirmation. (<$action> for instance <$id>)."
        sleep $SLEEP

        status=$( echo " select instanceeventaccepted from \"instances\" where instanceid = '$id'  " | psql -At )
        if [ "x$status" = 'xt' ]
        then
            flag='Receipt confirmed. Now we may leave the loop'

        fi 

        i=$(($i+1))
        if [ $i -ge $RETRIES ]
        then
            logger -p local0.notice -t NGW-MANAGE \
                "Manager failed to deliver event <$action> for instance <$id>."
            return 1
        fi
    done
    logger -p local0.notice -t NGW-MANAGE \
        "Manager delivered event <$action> for instance <$id>." 


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


logger -p local0.notice -t NGW-MANAGE \
    "Manager started with <$action>."

case $action in

    (create)
        export id="$1"
        class="$2"
        if test $# -gt 2; then name="$3"; else name="$1"; fi 

        event_tag="ngw/create"
        event_message="{ 'id': '${id}' , 'class': '${class}' , 'name': '${name}' }" 

        f_event "$event_message" "$event_tag"
        # Twice because the first event in a row gets lost between the minion and the master.
        # (I don't know why and how to fix it.)
        f_event "$event_message" "$event_tag"
        ;;

    (destroy)
        export id="$1" 
        event_tag="ngw/destroy"
        event_message="{ 'id': '${id}' }"

        f_event "$event_message" "$event_tag"
        # Twice because the first event in a row gets lost between the minion and the master.
        # (I don't know why and how to fix it.)
        f_event "$event_message" "$event_tag"
        
        ;;

    (*)
        logger -p local0.error -t NGW-MANAGE \
            "Manager was called for an unknown kind of event: <$action>"
        exit 1
        ;;

esac

exit 0
