nginx:
    pkg.installed:
        - name: nginx
    service.running:
        - name: nginx

/root/nginx-genconf.sh:
    file.managed:
        - source: salt://proxy/nginx-genconf.sh
        - mode: 755

/usr/bin/nginx-genconf.sh:
    file.symlink:
        - target: /root/nginx-genconf.sh

/root/nginx-rmconf.sh:
    file.managed:
        - source: salt://proxy/nginx-rmconf.sh
        - mode: 755

/usr/bin/nginx-rmconf.sh:
    file.symlink:
        - target: /root/nginx-rmconf.sh

