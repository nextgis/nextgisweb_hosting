nginx:
    pkg.installed:
        - name: nginx
    service.running:
        - name: nginx

{% set scripts = ['nginx-genconf.sh', 'nginx-rmconf.sh', 'call-create.sh'] %}

{% for script in scripts %}

/root/{{ script }}:
    file.managed:
        - source: salt://proxy/{{ script }}
        - mode: 755

/usr/bin/{{ script }}:
    file.symlink:
        - target: /root/{{ script }}

{% endfor %}

