{% set name = 'log' %}

/-{{ name }}:
    file.recurse:
        - name: / 
        - source: salt://{{ name }}/files
        - require:
            - file: /-all

/etc/rsyslog.d/10-ngw.conf:
    file.managed:
        - source: salt://log/files/etc/rsyslog.d/10-ngw.conf
    require:
        - file: /-{{ name }}

rsyslog-master:
    service:
        - name: rsyslog
        - running
        - enable: True
        - require:
            - file: /etc/rsyslog.d/10-ngw.conf
        - watch:
            - file: /etc/rsyslog.d/10-ngw.conf

