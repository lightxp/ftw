from django import template

register = template.Library()

@register.filter(name='tak_nie')
def tak_nie(value):
    "Zamienia 1 na TAK, 0 na NIE"
    if value == '0':
        return "NIE"
    else:
        return "TAK"
