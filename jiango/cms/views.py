# -*- coding: utf-8 -*-
# Created on 2015-10-13
# @author: Yefei
from django.http import Http404
from django.shortcuts import get_object_or_404
from jiango.shortcuts import renderer, incr_and_update_instance
from jiango.pagination import Paging
from .shortcuts import path_wrap
from .models import Path


render = renderer('cms/')


def content_render(current_path, content):
    path = current_path.selected
    if not content.is_available() or content.path != path:
        raise Http404()
    incr_and_update_instance(content, views=1)
    return path.content_template, 'content', dict(current_path=current_path, P=path, content=content, C=content)


@render
@path_wrap
def index(request, response, current_path):
    path = current_path.selected
    incr_and_update_instance(path, views=1)
    if path.default_view == Path.VIEW_CONTENT:
        model = path.get_model_object('model')
        if model is None:
            raise Http404()
        try:
            content = model.objects.available().filter(path=path).latest()
        except model.DoesNotExist:
            raise Http404()
        return content_render(current_path, content)
    elif path.default_view == Path.VIEW_LIST:
        return path.list_template, 'list', dict(current_path=current_path, P=path)
    return path.index_template, 'index', dict(current_path=current_path, P=path)


@render
@path_wrap
def content_list(request, response, current_path, page):
    path = current_path.selected
    incr_and_update_instance(path, views=1)
    model = path.get_model_object('model')
    if model is None:
        raise Http404()
    content_set = model.objects.available().filter(path=path)
    content_set = Paging(content_set, request, path.list_per_page).page()
    return path.list_template, 'list', dict(current_path=current_path, P=path, content_set=content_set, S=content_set)


@render
@path_wrap
def content_show(request, response, current_path, content_id):
    path = current_path.selected
    model = path.get_model_object('model')
    if model is None:
        raise Http404()
    content = get_object_or_404(model, pk=content_id)
    return content_render(current_path, content)
