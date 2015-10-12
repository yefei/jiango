# -*- coding: utf-8 -*-
# Created on 2015-10-8
# @author: Yefei
from django.conf.urls import url
from django.contrib import messages
from django.shortcuts import redirect
from jiango.admin.shortcuts import renderer, Logger, ModelLogger
from jiango.admin.auth import get_request_user
from .models import Column
from .forms import ColumnForm

render = renderer('cms/admin/')
log = Logger('cms')


@render
def index(request, response):
    return locals()


@render
def column(request, response):
    column_set = Column.objects.select_related('update_user').order_by('path')
    return locals()


@render
def column_edit(request, response, column_id=None):
    user = get_request_user(request)
    instance = Column.objects.get(pk=column_id) if column_id else None
    model_log = ModelLogger(instance)
    form = ColumnForm(request.POST or None, instance=instance)
    if form.is_valid():
        if not instance:
            form.instance.create_user = user
        form.instance.update_user = user
        obj = form.save()
        message = (instance and u'修改' or u'创建') + u'栏目: ' + unicode(obj)
        log.success(request, model_log.message(obj), log.CREATE)
        messages.success(request, message + u' 成功')
        return redirect('admin:cms:column')
    return locals()


@render
def content(request, response):
    return locals()


verbose_name = u'内容管理'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^column/$', column, name='column'),
    url(r'^column/create/$', column_edit, name='column-create'),
    url(r'^column/(?P<column_id>\d+)/$', column_edit, name='column-edit'),
    url(r'^content/$', content, name='content'),
]

PERMISSIONS = {
}
