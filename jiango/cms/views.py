# -*- coding: utf-8 -*-
# Created on 2015-10-13
# @author: Yefei
from jiango.shortcuts import renderer
from .util import column_path_wrap


render = renderer('cms/')


@render
@column_path_wrap
def column(request, response, column_select):
    column = column_select.selected
    return column.index_template or 'index', locals()


@render
@column_path_wrap
def content_list(request, response, column_select):
    column = column_select.selected
    return column.list_template or 'list', locals()


@render
@column_path_wrap
def content_show(request, response, column_select, content_id):
    column = column_select.selected
    return column.content_template or 'content', locals()
