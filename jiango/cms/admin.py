# -*- coding: utf-8 -*-
# Created on 2015-10-8
# @author: Yefei
from django.conf.urls import url
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, QueryDict
from jiango.shortcuts import update_instance
from jiango.pagination import Paging
from jiango.admin.shortcuts import renderer, Logger, ModelLogger, Alert, has_perm
from jiango.admin.auth import get_request_user
from .models import Column
from .utils import get_model_object, get_all_actions
from .shortcuts import column_path_wrap
from .forms import ColumnForm, ColumnEditForm, ActionForm, RecycleClearForm, ColumnDeleteForm
from .config import CONTENT_MODELS, CONTENT_ACTION_MAX_RESULTS, CONTENT_PER_PAGE


icon = 'fa fa-file-text-o'
verbose_name = u'内容管理'
render = renderer('cms/admin/')
log = Logger('cms')


@render
def column(request, response):
    column_set = Column.objects.select_related('update_user').order_by('path')
    return locals()


@render(perm='cms.column.edit')
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


@render(perm='cms.column.delete')
def column_delete(request, response, column_id):
    user = get_request_user(request)
    instance = Column.objects.get(pk=column_id)
    # 删除确认表单
    form = ColumnDeleteForm(request.POST or None)
    if form.is_valid():
        msg = u'删除栏目: ' + unicode(instance)
        logs = [msg, ModelLogger(instance).message()]
        # 删除子栏目
        for i in instance.children(-1):
            logs.append(u'子栏目: ' + unicode(i))
            logs.append(ModelLogger(i).message())
            i.delete()
        instance.delete()
        log.success(request, '\n'.join(logs), log.DELETE)
        messages.success(request, msg + u' 完成')
        return redirect('admin:cms:column')
    deleted_columns = [instance]
    deleted_columns.extend(list(instance.children(-1)))
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
            # 批量操作动作
            actions = column.get_content_actions()
            content_set = Model.objects.filter(is_deleted=False, column=column).select_related('update_user')
            content_set = Paging(content_set, request, CONTENT_PER_PAGE).page()
    else:
        # 没有选择任何栏目则统计已知模型中的数据
        pass
    return locals()


@render
def content_action(request, response):
    # 二次确认提交才有此值
    action_form_data = request.POST.get('__action_form_data')
    action_form_post = QueryDict(action_form_data) if action_form_data else request.POST
    
    # 判断批量选择数据是否合法
    action_form = ActionForm(action_form_post)
    if not action_form.is_valid():
        raise Alert(Alert.ERROR, action_form.errors)
    
    # 权限检查
    has_perm(request, 'cms.action.%s' % action_form.cleaned_data.get('action'))
    
    # 选定数据检查
    selected = action_form_post.getlist('pk')
    if not selected:
        raise Alert(Alert.ERROR, u'您没有勾选需要操作的内容')
    if len(selected) > CONTENT_ACTION_MAX_RESULTS:
        raise Alert(Alert.ERROR, u'超过最大选择条数: %d' % CONTENT_ACTION_MAX_RESULTS)
    
    # 为二次确认提交准备
    if not action_form_data:
        action_form_data = action_form_post.urlencode()
    
    back = action_form.cleaned_data.get('back')
    Model = action_form.get_model_object()
    Form = action_form.get_form_object()
    action_name = action_form.get_action_name()
    content_set = Model.objects.filter(pk__in=selected).select_related('column', 'update_user')
    
    if request.POST.get('__confirm') == 'yes':
        form = Form(content_set, request.POST, request.FILES)
        if form.is_valid():
            form.execute()
            msg = u'批量执行: ' + action_name
            log.success(request, u'%s\nID: %s\n表单数据: %s' % (msg, ','.join(selected), form.cleaned_data), form.log_action)
            messages.success(request, u'已完成' + msg)
            if back:
                return HttpResponseRedirect(back)
            return redirect('admin:cms:content')
    else:
        form = Form(content_set)
    return locals()


@render
def recycle(request, response, model=None):
    models = CONTENT_MODELS
    selected_model = models.get(model)
    # 无效的 model
    if model and selected_model is None:
        return redirect('admin:cms:recycle')
    
    if selected_model:
        Model = get_model_object(model, 'model')
        content_set = Model.objects.filter(is_deleted=True).select_related('column', 'update_user')
        
        if request.method == 'POST':
            action = request.POST.get('action')
            selected = request.POST.getlist('pk')
            if not selected:
                raise Alert(Alert.ERROR, u'您没有勾选需要操作的内容')
            if action == 'fire':
                has_perm(request, 'cms.recycle.fire')
                content_set.filter(pk__in=selected).delete()
                msg = u'回收站批量删除: ' + selected_model.get('name')
                log.success(request, u'%s\nID: %s' % (msg, ','.join(selected)), log.DELETE)
                messages.success(request, u'已完成' + msg)
        
        content_set = Paging(content_set, request, CONTENT_PER_PAGE).page()
    else:
        # 没有选择任何模型，则调用所有模型删除统计
        stats = {}
        total_count = 0
        for m, i in models.items():
            M = get_model_object(m, 'model')
            if not M:
                break
            count = M.objects.filter(is_deleted=True).count()
            total_count += count
            stats[m] = {'name': i.get('name'), 'count': count}
    return locals()


@render(perm='cms.recycle.clear')
def recycle_clear(request, response, model):
    is_clear_mode = True
    models = CONTENT_MODELS
    selected_model = models.get(model)
    model_name = selected_model.get('name')
    # 无效的 model
    if selected_model is None:
        return redirect('admin:cms:recycle')
    
    Model = get_model_object(model, 'model')
    content_set = Model.objects.filter(is_deleted=True)
    content_count = content_set.count()
    
    form = RecycleClearForm(content_count, request.POST or None)
    if form.is_valid():
        content_set.delete()
        msg = u'清空回收站: ' + model_name
        log.success(request, u'%s\n数量: %d' % (msg, content_count), log.DELETE)
        messages.success(request, u'已完成' + msg)
        return redirect('admin:cms:recycle')
    
    return 'recycle', locals()


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
    
    # 权限检查
    if not content:
        has_perm(request, 'cms.content.create')
    elif content.create_user == user:
        has_perm(request, 'cms.content.update.self')
    else:
        has_perm(request, 'cms.content.update.other')
    
    # 删除操作
    delete_id = request.GET.get('delete')
    if content and not content.is_deleted and content_id == delete_id:
        has_perm(request, 'cms.action.delete')
        update_instance(content, is_deleted=True)
        log.success(request, model_log.message(content), log.DELETE)
        messages.success(request, u'删除内容: %s 成功' % unicode(content))
        return redirect('admin:cms:content-path', column.path)
    
    # 删除恢复
    recover_id = request.GET.get('recover')
    if content and content.is_deleted and content_id == recover_id:
        has_perm(request, 'cms.content.recover')
        update_instance(content, is_deleted=False)
        log.success(request, model_log.message(content), log.UPDATE)
        messages.success(request, u'恢复删除内容: %s 成功' % unicode(content))
        return redirect('admin:cms:content-path', column.path)
    
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
            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET.get('next'))
            return redirect('admin:cms:content-path', column.path)
    else:
        form = Form(instance=content)
    
    # 表单字段分离
    main_fields = []
    meta_fields = []
    meta_fields_name = ['is_hidden']
    _t = column.get_model_object('form_meta_fields')
    if _t:
        meta_fields_name.extend(_t)
    
    for i in form.visible_fields():
        if i.name in meta_fields_name:
            meta_fields.append(i)
        else:
            main_fields.append(i)
    
    return 'content', locals()


urlpatterns = [
    url(r'^$', content, name='index'),
    url(r'^/column$', column, name='column'),
    url(r'^/column/create$', column_edit, name='column-create'),
    url(r'^/column/(?P<column_id>\d+)$', column_edit, name='column-edit'),
    url(r'^/column/(?P<column_id>\d+)/delete$', column_delete, name='column-delete'),
    
    url(r'^/content$', content, name='content'),
    url(r'^/content/path/(?P<path>.*)$', content, name='content-path'),
    url(r'^/content/create/(?P<path>.*)$', content_edit, name='content-create'),
    url(r'^/content/edit/(?P<path>.*)/(?P<content_id>\d+)$', content_edit, name='content-edit'),
    url(r'^/content/action$', content_action, name='content-action'),
    
    url(r'^/recycle$', recycle, name='recycle'),
    url(r'^/recycle/(?P<model>\w+)$', recycle, name='recycle-model'),
    url(r'^/recycle/(?P<model>\w+)/clear$', recycle_clear, name='recycle-model-clear'),
]

PERMISSIONS = {
    'column.edit': u'栏目|创建/编辑',
    'column.delete': u'栏目|删除',
    'recycle.fire': u'回收站|批量删除',
    'recycle.clear': u'回收站|清空',
    'content.create': u'内容|创建',
    'content.update.self': u'内容|修改本人内容',
    'content.update.other': u'内容|修改他人内容',
    'content.recover': u'内容|删除恢复',
}


# 批量操作权限
def _load_actions():
    for a, i in get_all_actions().items():
        perm = 'action.%s' % a
        PERMISSIONS[perm] = u'内容|%s' % i['name']
_load_actions()
