{# {% if data['id'] == 'proxy.ngw' %} #}

{% set keys = ['id', 'backup'] %} 
{# This list corresponds exactly to the structure sent #}
{# by the event and the parameters used by the runner. #} 
{% set values = data['data'] %}


runner:
    runner.ngw.restore:
{% for key in keys %}
        - {{ key }}: {{ values[key] }}
{%- endfor %}

{# {% endif %} #}



