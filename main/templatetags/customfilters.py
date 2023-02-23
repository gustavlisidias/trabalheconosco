from django import template

register = template.Library()
@register.filter(is_safe=True)
def conversor(value):
    return hex(value+3109786745873612405294780)[2:]