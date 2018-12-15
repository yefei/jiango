# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/4/11
"""
from django.template import Library
from jiango.importlib import import_object
from jiango.cms.shortcuts import get_current_path, PathDoesNotExist
from jiango.cms.models import Collection, CollectionContent
from jiango.cms.config import CONTENT_MODELS


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
    qs = model.objects.available().filter(path=path).order_by('-contentbase_ptr__id')
    if filters:
        qs = qs.filter(**filters)
    if excludes:
        qs = qs.exclude(**excludes)
    content_set = qs[offset:offset+limit]
    return content_set


@register.assignment_tag
def cms_collections(name, limit=10, offset=0, **kwargs):
    obj, created = Collection.objects.get_or_create(name=name)
    results = []
    vs = []
    if not created:
        qs = obj.contentbase_set.filter(is_deleted=False, is_hidden=False)
        qs = qs[offset:offset+limit]
        vs = qs.values_list('pk', 'model')
    if vs:
        # 根据检索出的ID 和 模型批量取得模型数据
        models = {}
        for pk, model in vs:
            if model not in models:
                models[model] = []
            models[model].append(pk)
        _results = {}
        for model, pks in models.items():
            model_class = import_object(CONTENT_MODELS.get(model)['model'])
            for i in model_class.objects.filter(pk__in=pks):
                _results[i.pk] = i
        # 按照内容顺序插入
        for pk, model in vs:
            results.append(_results[pk])
    return results
