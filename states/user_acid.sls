{% for user_id in ['acid'] %}


{{user_id}}-user:
  user.present:
    - name: {{user_id}}
    - groups:
      - sudo

{{user_id}}-ssh-dir:
  file.directory:
    - name: /home/{{user_id}}/.ssh
    - mode: 700 
    - user: {{user_id}}
    - require:
      - user: {{user_id}}

{{user_id}}-ssh-keys:
  file.managed:
    - name: /home/{{user_id}}/.ssh/authorized_keys
    - source: salt://user.{{user_id}}/keys.{{user_id}}
    - mode: 600
    - user: {{user_id}}
    - require:
      - file: /home/{{user_id}}/.ssh

{{user_id}}-home:
  file.recurse:
    - name: /home/{{user_id}}
    - source: salt://user.{{user_id}}/home.{{user_id}}
    - require:
      - user: {{user_id}}

{% endfor %}
