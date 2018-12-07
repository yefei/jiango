# -*- coding: utf-8 -*-
# Created on 2015-10-13
# @author: Yefei
from functools import wraps
from django.http import Http404
from .models import Path


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
