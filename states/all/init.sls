/-all:
    file.recurse:
        - name: /
        - source: salt://all/files

{% set files = ['/etc/rsyslog.d/80-ngw-minion.conf', '/etc/ssh/sshd_config'] %}
{# This is a way to hook service watch statements. #}
{% for file in files %} 
{{ file }}:

    file.managed:
        - source: salt://all/files/{{ file }}
        - require:
            - file: / 

{% endfor %}

rsyslog: 
    pkg.installed:
        - name: rsyslog
    service:
        - running
        - enable: True
        - require:
            - file: /etc/rsyslog.d/80-ngw-minion.conf
            - pkg: rsyslog
        - watch:
            - file: /etc/rsyslog.d/80-ngw-minion.conf

ssh: 
    pkg.installed:
        - name: ssh
    service:
        - running
        - enable: True
        - require:
            - file: /etc/ssh/sshd_config
            - pkg: ssh
        - watch:
            - file: /etc/ssh/sshd_config

zsh:
    pkg.installed:
        - name: zsh
{#
    git.latest:
        - name: git://github.com/zsh-users/zsh-syntax-highlighting.git
        - target: /usr/share/zsh/plugins/zsh-syntax-highlighting
#}
    


root:
    user.present:
        - password: '!'
        - shell: /bin/zsh

salt:
    group.present

{#
/etc/salt:
    file.directory:
        - user: root
        - group: salt
        - recurse:
            - user
            - group
        - require:
            - group: salt

/etc/salt/pki/minion:
    file.directory:
        - mode: 750

/etc/salt/pki/minion/minion.pem:
    file.managed:
        - mode: 640

/var/cache/salt:
    file.directory:
        - user: root
        - group: salt
        - recurse:
            - user
            - group
        - require:
            - group: salt
#}

