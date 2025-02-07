
from smolagents import GradioUI, {{ class_name }}, {{ agent_dict['model']['class'] }}

{% for tool in tools.values() %}
from scripts.{{ tool.name }} import {{ tool.__class__.__name__ }}
{% endfor %}

model = {{ agent_dict['model']['class'] }}()

{% for tool in tools.values() %}
{{ tool.name }} = {{ tool.__class__.__name__ }}()
{% endfor %}

agent = {{ class_name }}(
    model=model,
    tools=[{% for tool in tools.keys() %}{{ tool }}{% if not loop.last %}, {% endif %}{% endfor %}],
    {% for attribute_name, value in agent_dict.items() if attribute_name not in ["model", "tools", "prompt_templates"] %}
    {{ attribute_name }}={{ value }},
    {% endfor %}
    prompts_path='./prompts.yaml'
)

GradioUI(agent).launch()
