# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/4/11
"""
from django.template import Library
from jiango.cms.shortcuts import get_current_path, PathDoesNotExist


register = Library()


@register.assignment_tag
def cms_contents(path, limit=10, offset=0, **kwargs):
    try:
        current_path = get_current_path(path)
    except PathDoesNotExist:
        return []
    path = current_path.selected
    model = path.model_class
    if model is None:
        return []
    filters = {}
    excludes = {}
    for k, v in kwargs.items():
        if k.startswith('not__'):
            excludes[k[5:]] = v
        else:
            filters[k] = v
    qs = model.objects.available().filter(path=path)
    if filters:
        qs = qs.filter(**filters)
    if excludes:
        qs = qs.exclude(**excludes)
    content_set = qs[offset:offset+limit]
    return content_set
