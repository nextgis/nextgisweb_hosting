/-all:
    file.recurse:
        - name: /
        - source: salt://all/files

{% set files = ['/etc/rsyslog.d/80-ngw-minion.conf', '/etc/ssh/sshd_config'] %}
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
        - require:
            - git: zsh-syntax-highlighting

zsh-syntax-highlighting:
    git.present:
        - name: https://github.com/zsh-users/zsh-syntax-highlighting
        - target: /usr/share/zsh/plugins/zsh-syntax-highlighting
    


root:
    user.present:
        - password: '!'
        - shell: /bin/zsh

