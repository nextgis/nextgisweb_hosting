/etc/rsyslog.d/ngw-minion.conf:
    file.managed:
        - source: salt://all/ngw-minion.conf

/etc/salt/minion:
    file.managed:
        - source: salt://all/minion

rsyslog: 
    service:
        - running
        - require:
            - file: /etc/rsyslog.d/ngw-minion.conf
        - watch:
            - file: /etc/rsyslog.d/ngw-minion.conf

