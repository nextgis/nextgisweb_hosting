{% set name = 'proxy' %}

/-{{ name }}:
    file.recurse:
        - name: / 
        - source: salt://{{ name }}/files
        - require:
            - file: /-all

/etc/sudoers:
    file.managed:
        - source: salt://{{ name }}/files/etc/sudoers
        - require:
            - file: /-{{ name }}
        - permissions: 440

nginx:
    pkg.installed:
        - name: nginx
    service.running:
        - name: nginx

