# -*- coding: utf-8 -*-
# Created on 2016-4-8
# @author: Yefei
from django import template

register = template.Library()


@register.simple_tag(takes_context=True, name='ff')
def form_field(context, field, error_class=None, **attrs):
    u""" 自定义 form field 中的 attr
        {% ff form.mobile "errorClassName" type="tel" placeholder="请输入手机号" %}
    """
    if error_class and field.errors:
        attrs['class'] = (attrs.get('class','') + ' ' + error_class).strip()
    return field.as_widget(attrs=attrs)
