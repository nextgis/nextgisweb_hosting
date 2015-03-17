base:

    '*':
        - all

    'instance-*.ngw':
        - instance
        - users
    'tempora-*.ngw':
        - instance
        - users

    'dday.ngw':
        - instance
        - users


{% set hosts = ['db-precise', 'gate', 'log', 'ns1', 'proxy', 'salt'] %}
{% for host in hosts %}
    '{{ host }}.ngw':
        - {{ host }}
{% endfor %}

    'master-18':
        - master-18
        - openvpn_tap_server
        - user_acid

    'master-20':
        - master-20
        - users 
        - openvpn_tap_client
        - machineer-host

    
    'tempora-lash-183.ngw':
        - users


    'api-amjad-01.ngw':
        - 'user_acid'
