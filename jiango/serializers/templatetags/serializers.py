# -*- coding: utf-8 -*-
# Created on 2015-9-22
# @author: Yefei
from django import template
from django.utils.safestring import mark_safe
from jiango.serializers import serialize


register = template.Library()


@register.filter('serialize')
def do_serialize(var, toformat):
    return mark_safe(serialize(toformat, var))


@register.filter
def json(var):
    return mark_safe(serialize('json', var))


@register.filter
def yaml(var):
    return mark_safe(serialize('yaml', var))
