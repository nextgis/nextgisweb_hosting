/etc/init/ngw-uwsgi.conf:
    file.managed:
        - source: salt://instance/ngw-uwsgi.conf

ngw-uwsgi:
    service:
        - running
        - enable: True
        - require:
            - file: /etc/init/ngw-uwsgi.conf
        - watch:
            - file: /etc/init/ngw-uwsgi.conf

