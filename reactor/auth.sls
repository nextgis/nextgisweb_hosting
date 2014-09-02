{#
{% if 'act' in data and data['act'] == 'pend' and data['id'].startswith('instance-') %}

minion_add:
    wheel.key.accept:
        - match: {{ data['id'] }}

{% endif %}
#}
