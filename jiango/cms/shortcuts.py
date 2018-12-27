# -*- coding: utf-8 -*-
# Created on 2015-10-13
# @author: Yefei
from functools import wraps
from django.http import Http404
from jiango.importlib import import_object
from .models import Path, Collection
from .config import CONTENT_MODELS


class PathDoesNotExist(Exception):
    def __init__(self, path):
        self.path = path


class CurrentPath(object):
    def __init__(self, tree):
        self.tree = tree  # 数据库返回的树形路径结构
        self.breadcrumb = []  # 当前路径导航
        self.currents = []  # 当前路径同级别其他路径项
        self.children = []  # 当前路径子路径列表
        self.selected = None  # 当前路径对象
        self.path = ''  # 当前路径
    
    def select(self, path=''):
        if path:
            self.path = path
            ref = self.tree
            _path = []
            parent = None
            for slug in path.split('/'):
                parent = ref
                _path.append(slug)
                try:
                    col, ref = ref[slug]
                except KeyError:
                    raise PathDoesNotExist('/'.join(_path))
                self.breadcrumb.append(col)
            for i in parent.values():
                self.currents.append(i[0])
            self.selected = self.breadcrumb[-1]
            for i in ref.values():
                self.children.append(i[0])
        else:
            for i in self.tree.values():
                self.children.append(i[0])


def get_current_path(path):
    path_tree = Path.objects.cached_tree()
    current_path = CurrentPath(path_tree)
    current_path.select(path)
    return current_path


def flat_path_tree(path_tree):
    paths = []
    for p, c in path_tree.values():
        paths.append(p)
        if c:
            paths.extend(flat_path_tree(c))
    return paths


def path_wrap(func):
    @wraps(func)
    def wrapper(request, response, path='', *args, **kwargs):
        try:
            current_path = get_current_path(path)
        except PathDoesNotExist:
            raise Http404()
        return func(request, response, current_path, *args, **kwargs)
    return wrapper


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
