/etc/init/ngw-uwsgi.conf:
    file.managed:
        - source: salt://instance/ngw-uwsgi.conf
