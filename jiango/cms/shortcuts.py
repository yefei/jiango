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
        self.tree = tree
        self.breadcrumb = []
        self.children = []
        self.selected = None
        self.path = ''
    
    def select(self, path=''):
        if path:
            self.path = path
            ref = self.tree
            _path = []
            for slug in path.split('/'):
                _path.append(slug)
                try:
                    col, ref = ref[slug]
                except KeyError:
                    raise PathDoesNotExist('/'.join(_path))
                self.breadcrumb.append(col)
            self.selected = self.breadcrumb[-1]
            for i in ref.values():
                self.children.append(i[0])
        else:
            for i in self.tree.values():
                self.children.append(i[0])


def path_wrap(func):
    @wraps(func)
    def wrapper(request, response, path='', *args, **kwargs):
        path_tree = Path.objects.tree()
        current_path = CurrentPath(path_tree)
        try:
            current_path.select(path)
        except PathDoesNotExist:
            raise Http404()
        return func(request, response, current_path, *args, **kwargs)
    return wrapper
