{% set name = 'gate' %}

/-{{ name }}:
    file.recurse:
        - name: / 
        - source: salt://{{ name }}/files
        - require:
            - file: /-all

/etc/dnsmasq.conf:
    file.managed:
        - source: salt://gate/files/etc/dnsmasq.conf
    require:
        - file: /-{{ name }}

dnsmasq:
    service:
        - running
        - enable: True
        - require:
            - file: /etc/dnsmasq.conf
        - watch:
            - file: /etc/dnsmasq.conf

