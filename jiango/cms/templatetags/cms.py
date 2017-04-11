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
    model = path.get_model_object('model')
    if model is None:
        return []
    content_set = model.objects.available().filter(path=path, **kwargs)[offset:offset+limit]
    return content_set
