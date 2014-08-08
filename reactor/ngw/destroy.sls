{% if data['id'] == 'proxy.ngw' %}

{#
destroy_database:
    cmd.cmd.run:
        - tgt: db-precise.ngw
        - arg:
            - pg_erase.sh {{ data['data']['database'] }} {{ data['data']['username'] }}

destroy_container:
    cmd.cmd.run:
        - tgt: master-18
        - arg:
          - lxc-rmconf.sh {{ data['data']['container'] }}
#}

runner:
    runner.ngw.destroy:
        - database: {{ data['data']['database'] }}
        - username: {{ data['data']['username'] }}
        - container: {{ data['data']['container'] }}


{% endif %}
