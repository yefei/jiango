# -*- coding: utf-8 -*-
# Created on 2015-10-13
# @author: Yefei
from functools import wraps
from django.http import Http404
from .models import Column


class ColumnPathDoesNotExist(Exception):
    def __init__(self, path):
        self.path = path


class ColumnSelect(object):
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
                    raise ColumnPathDoesNotExist('/'.join(_path))
                self.breadcrumb.append(col)
            self.selected = self.breadcrumb[-1]
            for i in ref.values():
                self.children.append(i[0])
        else:
            for i in self.tree.values():
                self.children.append(i[0])


def column_path_wrap(func):
    @wraps(func)
    def wrapper(request, response, path='', *args, **kwargs):
        column_tree = Column.objects.tree()
        column_select = ColumnSelect(column_tree)
        try:
            column_select.select(path)
        except ColumnPathDoesNotExist:
            raise Http404()
        return func(request, response, column_select, *args, **kwargs)
    return wrapper
