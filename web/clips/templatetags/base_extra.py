from django import template

register = template.Library()

@register.simple_tag
def active_page(request, view_name):
    from django.core.urlresolvers import resolve, Resolver404
    if not request:
        return ""
    try:
        return "active" if resolve(request.path_info).url_name == view_name else ""
    except Resolver404:
        return ""

@register.simple_tag
def active_page_GET(request, view_name, parameter):
    try:
        x = request.GET[parameter]
    except KeyError:
        x = ""
    return "active" if x == view_name else ""
