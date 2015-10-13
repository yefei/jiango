# -*- coding: utf-8 -*-
# Created on 2015-10-8
# @author: Yefei
from django.conf.urls import url
from django.contrib import messages
from django.shortcuts import redirect
from jiango.pagination import Paging
from jiango.admin.shortcuts import renderer, Logger, ModelLogger, Alert
from jiango.admin.auth import get_request_user
from .util import column_path_wrap
from .models import Column
from .forms import ColumnForm, ColumnEditForm

render = renderer('cms/admin/')
log = Logger('cms')


@render
def column(request, response):
    column_set = Column.objects.select_related('update_user').order_by('path')
    return locals()


@render
def column_edit(request, response, column_id=None):
    user = get_request_user(request)
    instance = Column.objects.get(pk=column_id) if column_id else None
    model_log = ModelLogger(instance)
    Form = ColumnEditForm if instance and instance.model else ColumnForm
    form = Form(request.POST or None, instance=instance)
    if form.is_valid():
        if not instance:
            form.instance.create_user = user
        form.instance.update_user = user
        obj = form.save()
        log.success(request, model_log.message(obj), log.CREATE)
        messages.success(request, (instance and u'修改' or u'创建') + u'栏目: ' + unicode(obj) + u' 成功')
        return redirect('admin:cms:column')
    return locals()


@render
@column_path_wrap
def content(request, response, column_select):
    can_create_content = False
    column = column_select.selected
    if column:
        Model = column.get_model_object('model')
        if Model:
            can_create_content = True
            content_set = Model.objects.filter(column=column).select_related('update_user')
            content_set = Paging(content_set, request).page()
    else:
        # 没有选择任何栏目则统计已知模型中的数据
        pass
    return locals()


@render
@column_path_wrap
def content_edit(request, response, column_select, content_id=None):
    user = get_request_user(request)
    is_content_edit = True
    column = column_select.selected
    
    Model = column.get_model_object('model')
    Form = column.get_model_object('form')
    if Model is None or Form is None:
        raise Alert(Alert.ERROR, u'此栏目 %s 不可添加内容' % column)
    
    content = Model.objects.get(column=column, pk=content_id) if content_id else None
    model_log = ModelLogger(content)
    
    if request.method == 'POST':
        form = Form(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.instance.column = column
            form.instance.column_path = column.path
            form.instance.column_depth = column.depth
            if not form.instance.create_user:
                form.instance.create_user = user
            form.instance.update_user = user
            obj = form.save()
            
            log.success(request, model_log.message(obj), log.CREATE)
            messages.success(request, (content and u'修改' or u'创建') + u'内容: ' + unicode(obj) + u' 成功')
            return redirect('admin:cms:content-path', column.path)
    else:
        form = Form(instance=content)
    return 'content', locals()


verbose_name = u'内容管理'

urlpatterns = [
    url(r'^$', content, name='index'),
    url(r'^column/$', column, name='column'),
    url(r'^column/create/$', column_edit, name='column-create'),
    url(r'^column/(?P<column_id>\d+)/$', column_edit, name='column-edit'),
    url(r'^content/$', content, name='content'),
    url(r'^content/path/(?P<path>.*)/$', content, name='content-path'),
    url(r'^content/create/(?P<path>.*)/$', content_edit, name='content-create'),
    url(r'^content/edit/(?P<path>.*)/(?P<content_id>\d+)/$', content_edit, name='content-edit'),
]

PERMISSIONS = {
}
