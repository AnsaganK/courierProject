from django import template

register = template.Library()


@register.filter(name='line_entry')
def line_entry(string1, string2):
    return True if string1 in string2 else False


# Refactor
@register.filter(name='to_str')
def to_str(value):
    return str(value)
