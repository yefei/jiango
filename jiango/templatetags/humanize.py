# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
from django import template
from jiango.utils.humanize import humanize_second, humanize_size


register = template.Library()
register.filter('humanizesecond', humanize_second, is_safe=True)


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


@register.filter(is_safe=True)
def intcomma(value):
    return '{:,}'.format(value)
