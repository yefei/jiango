# -*- coding: utf-8 -*-
# Created on 2015-10-13
# @author: Yefei
from django.http import Http404
from django.shortcuts import get_object_or_404
from jiango.shortcuts import renderer, incr_and_update_instance
from .util import column_path_wrap


render = renderer('cms/')


@render
@column_path_wrap
def column(request, response, column_select):
    column = column_select.selected
    breadcrumb = column_select.breadcrumb
    incr_and_update_instance(column, views=1)
    return column.index_template, 'index', locals()


@render
@column_path_wrap
def content_list(request, response, column_select):
    column = column_select.selected
    breadcrumb = column_select.breadcrumb
    incr_and_update_instance(column, views=1)
    return column.list_template, 'list', locals()


@render
@column_path_wrap
def content_show(request, response, column_select, content_id):
    column = column_select.selected
    breadcrumb = column_select.breadcrumb
    Model = column.get_model_object('model')
    if Model is None:
        raise Http404()
    content = get_object_or_404(Model.objects.available(), pk=content_id)
    incr_and_update_instance(content, views=1)
    return column.content_template, 'content', locals()
