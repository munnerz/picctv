from django import template
import time

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

@register.filter
def naturalTimeDifference(value):
    """
    Finds the difference between the datetime value given and now()
    and returns appropriate humanize form
    """
    
    from datetime import datetime
    MOMENT = 30

    if isinstance(value, datetime):
        delta = datetime.now() - value
        if delta.days > 6:
            return value.strftime("%b %d")                    # May 15
        if delta.days > 1:
            return value.strftime("%A")                       # Wednesday
        elif delta.days == 1:
            return 'yesterday'                                # yesterday
        elif delta.seconds > 3600:
            return str(delta.seconds / 3600 ) + ' hours ago'  # 3 hours ago
        elif delta.seconds >  MOMENT:
            return str(delta.seconds/60) + ' minutes ago'     # 29 minutes ago
        else:
            return 'a moment ago'                             # a moment ago
        return defaultfilters.date(value)
    else:
        return str(value)

@register.filter
def epoch(value):
    try:
        return int(time.mktime(value.timetuple()))
    except AttributeError:
        return ''