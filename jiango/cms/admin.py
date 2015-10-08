# -*- coding: utf-8 -*-
# Created on 2015-10-8
# @author: Yefei
from django.conf.urls import url
from jiango.admin.shortcuts import renderer, Logger

render = renderer('cms/admin/')
log = Logger('cms')


@render
def index(request, response):
    return locals()


@render
def column(request, response):
    return locals()


@render
def content(request, response):
    return locals()


verbose_name = u'内容管理系统'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^column/$', column, name='column'),
    url(r'^content/$', content, name='content'),
]

PERMISSIONS = {
}
