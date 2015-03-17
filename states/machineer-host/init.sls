{% set name = 'machineer-host' %}

/-{{ name }}:
    file.recurse:
        - name: / 
        - source: salt://{{ name }}/files
        - require:
            - file: /-all

{# LVM #}

{% set lvm_pvsize = '1T' %}
{% set lvm_vg = 'master-20' %}
{% set lvm_dir = '/var/lvm' %}
{% set lvm_loop = '/dev/loop0' %}


losetup:
  file.directory:
    - name: {{lvm_dir}}
  cmd.run:
    - name: fallocate -l {{lvm_pvsize}} {{lvm_dir}}/{{lvm_vg}}
    - unless: stat {{lvm_dir}}/{{lvm_vg}}

lvm-pv:
  lvm.pv_present:
    - name: {{lvm_loop}}

lvm-vg:
  lvm.vg_present:
    - name: {{lvm_vg}}
    - devices: /dev/loop0


lxc:
  pkg.installed:
    - name: lxc

python-dbus:
  pkg.installed
