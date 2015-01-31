{# {% if data['id'] == 'proxy.ngw' %} #}

{% set keys = ['id'] %} 
{# This list corresponds exactly to the structure sent #}
{# by the event and the parameters used by the runner. #} 
{% set values = data['data'] %}


runner:
    runner.ngw.backup:
{% for key in keys %}
        - {{ key }}: {{ values[key] }}
{%- endfor %}

{# {% endif %} #}


