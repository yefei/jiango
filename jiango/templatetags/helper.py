# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/9/2
"""
from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import capfirst


register = template.Library()


def order_by(order, fields, default='-id'):
    u"""
    检查排序参数是否包含在 fields 中，并检查是否正确
    :param order: 请求的排序参数
    :param fields: 允许的排序字段
    :param default: 默认排序字段，不符合规则时返回
    :return: 返回最终排序字段
    """
    if order:
        if order[0] == '-':
            f = order[1:]
        else:
            f = order
        if f in fields:
            return order
    return default


@register.simple_tag(takes_context=True)
def order_by_tag(context, order, field, verbose_name=None, key='order', page_field='page'):
    verbose_name = verbose_name or capfirst(field)
    order_display = ''
    order_field = '-%s' % field
    if order:
        if order[0] == '-':
            order = order[1:]
            desc = True
        else:
            desc = False
        if order == field:
            order_display = u' ↓' if desc else u' ↑'
            if desc:
                order_field = field
    request = context.get('request')
    get_vars = request.GET.copy() if request else {}
    get_vars[key] = order_field
    get_vars.pop(page_field, None)
    return mark_safe('<a href="?%s">%s</a>%s' % (get_vars.urlencode(), verbose_name, order_display))


@register.filter('min')
def _min(v, min_v):
    if not v:
        return v
    return min(v, min_v)


@register.filter
def startswith(v, prefix):
    if not v:
        return False
    return v.startswith(prefix)
