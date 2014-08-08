{% if data['id'] == 'proxy.ngw' %}

runner:
    runner.ngw.create:
        - database: {{ data['data']['database'] }}
        - username: {{ data['data']['username'] }}
        - password: {{ data['data']['password'] }}
        - identifier: {{ data['data']['identifier'] }}
        - image: {{ data['data']['image'] }}
        - hostname: {{ data['data']['hostname'] }}

{% endif %}
