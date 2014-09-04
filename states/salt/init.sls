{% set name = 'salt' %}

/-{{ name }}:
    file.recurse:
        - name: / 
        - source: salt://{{ name }}/files
        - require:
            - file: /-all

