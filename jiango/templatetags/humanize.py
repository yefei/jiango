# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
from django import template
from jiango.utils.humanize import humanize_second, humanize_size, intcomma4, timesince_single


register = template.Library()
register.filter('humanizesecond', humanize_second, is_safe=True)
register.filter(intcomma4)


@register.filter(is_safe=True)
def naturalsecond(seconds):
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return ''.join(((u'%d天' % days if days else ''),
                    (u'%d小时' % hours if hours else ''),
                    (u'%d分钟' % minutes if minutes else ''),
                    (u'%d秒' % seconds if seconds else ''),
                    ))


@register.filter(is_safe=True)
def filesize(value):
    size, unit = humanize_size(int(value))
    if unit is None:
        return size
    return '%.2f %sB' %(size, unit)


@register.filter("timesince_single", is_safe=False)
def timesince_single_filter(value, arg=None):
    """Formats a date as the time since that date (i.e. "4 days")."""
    if not value:
        return u''
    try:
        if arg:
            return timesince_single(value, arg)
        return timesince_single(value)
    except (ValueError, TypeError):
        return u''
