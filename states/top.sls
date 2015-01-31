base:

    '*':
        - all

    'instance-*.ngw':
        - instance
    'tempora-*.ngw':
        - instance

{% set hosts = ['db-precise', 'gate', 'log', 'ns1', 'proxy', 'salt'] %}
{% for host in hosts %}
    '{{ host }}.ngw':
        - {{ host }}
{% endfor %}

    'master-18':
        - master-18
        - openvpn_tap_server

    'master-20':
        - master-20
        - users 
        - openvpn_tap_client

    
    'tempora-lash-183.ngw':
        - users

