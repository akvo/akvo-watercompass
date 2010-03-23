
from django import template
register = template.Library()

# http://stackoverflow.com/questions/250357/smart-truncate-in-python 
@register.filter
def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0]+suffix