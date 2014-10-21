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
    service:
      - running
      - enable: True
      - watch:
        - file: /-{{ name }}

ngw-flask:
  service:
    - running
    - enable: True
    - watch:
      - file: /-{{ name }}

