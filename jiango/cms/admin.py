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
from .models import Path, ContentBase
from .shortcuts import path_wrap, flat_path_tree, get_current_path
from .forms import PathForm, ActionForm, PathDeleteForm
from .config import CONTENT_ACTION_MAX_RESULTS, CONTENT_PER_PAGE, CONTENT_ACTIONS


icon = 'fa fa-file-text-o'
verbose_name = u'内容'
render = renderer('cms/admin/')
log = Logger('cms')


@render
def index(request, response):
    return redirect('admin:cms:content')


@render
def path(request, response):
    path_tree = Path.objects.select_related('update_user').tree()
    path_set = flat_path_tree(path_tree)
    return locals()


@render(perm='cms.path.edit')
def path_edit(request, response, path_id=None):
    user = get_request_user(request)
    instance = Path.objects.get(pk=path_id) if path_id else None
    model_log = ModelLogger(instance)
    form = PathForm(request.POST or None, instance=instance)
    if form.is_valid():
        if not instance:
            form.instance.create_user = user
        form.instance.update_user = user
        obj = form.save()
        log.success(request, model_log.message(obj), log.CREATE)
        messages.success(request, (instance and u'修改' or u'创建') + u'栏目: ' + unicode(obj) + u' 成功')
        return redirect('admin:cms:path')
    return locals()


@render(perm='cms.path.delete')
def path_delete(request, response, path_id):
    user = get_request_user(request)
    instance = Path.objects.get(pk=path_id)
    # 删除确认表单
    form = PathDeleteForm(request.POST or None)
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
        return redirect('admin:cms:path')
    deleted_paths = [instance]
    deleted_paths.extend(list(instance.children(-1)))
    return locals()


@render
@path_wrap
def content(request, response, current_path):
    can_create_content = False
    paths = flat_path_tree(Path.objects.tree())
    path = current_path.selected
    actions = CONTENT_ACTIONS
    content_set = ContentBase.objects.filter(is_deleted=False)
    total_content_count = content_set.count()
    if path:
        can_create_content = True
        content_set = content_set.filter(path=path)
    else:
        content_set = content_set.select_related('path')
    content_set = content_set.select_related('update_user')
    content_set = Paging(content_set, request, CONTENT_PER_PAGE).page()
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
    Form = action_form.get_form_object()
    action_name = action_form.get_action_name()
    content_set = ContentBase.objects.filter(pk__in=selected).select_related('path', 'update_user')
    
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
def recycle(request, response):
    content_set = ContentBase.objects.filter(is_deleted=True).select_related('path', 'update_user')
    if request.method == 'POST':
        action = request.POST.get('action')
        selected = request.POST.getlist('pk')
        if not selected:
            raise Alert(Alert.ERROR, u'您没有勾选需要操作的内容')
        if action == 'fire':
            has_perm(request, 'cms.recycle.fire')
            content_set.filter(pk__in=selected).delete()
            msg = u'回收站批量删除'
            log.success(request, u'%s\nID: %s' % (msg, ','.join(selected)), log.DELETE)
            messages.success(request, u'已完成' + msg)
    content_set = Paging(content_set, request, CONTENT_PER_PAGE).page()
    return locals()


@render(perm='cms.recycle.clear')
def recycle_clear(request, response):
    is_clear_mode = True
    content_set = ContentBase.objects.filter(is_deleted=True)
    content_count = content_set.count()
    if request.method == 'POST':
        content_set.delete()
        msg = u'清空回收站'
        log.success(request, u'%s\n数量: %d' % (msg, content_count), log.DELETE)
        messages.success(request, u'已完成' + msg)
        return redirect('admin:cms:recycle')
    return 'recycle', locals()


def _content_edit(request, response, current_path=None, content_id=None):
    user = get_request_user(request)
    is_content_edit = True

    if content_id:
        content_base = ContentBase.objects.get(pk=content_id)
        Model = content_base.model_class
        Form = content_base.form_class
        path = content_base.path
        content = Model.objects.get(pk=content_id)
        current_path = get_current_path(path.path)
    elif current_path:
        path = current_path.selected
        Model = path.model_class
        Form = path.form_class
        content = None
    else:
        raise Alert(Alert.ERROR, u'缺少必要参数')

    if Form is None:
        raise Alert(Alert.ERROR, u'此栏目 %s 不可添加内容' % path)

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
        return redirect('admin:cms:content-path', path.path)
    
    # 删除恢复
    recover_id = request.GET.get('recover')
    if content and content.is_deleted and content_id == recover_id:
        has_perm(request, 'cms.content.recover')
        update_instance(content, is_deleted=False)
        log.success(request, model_log.message(content), log.UPDATE)
        messages.success(request, u'恢复删除内容: %s 成功' % unicode(content))
        return redirect('admin:cms:content-path', path.path)
    
    if request.method == 'POST':
        form = Form(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.instance.path = path
            form.instance.path_value = path.path
            form.instance.path_depth = path.depth
            if not form.instance.model:
                form.instance.model = path.model
            if not form.instance.create_user:
                form.instance.create_user = user
            form.instance.update_user = user
            obj = form.save()
            
            log.success(request, model_log.message(obj), log.CREATE)
            messages.success(request, (content and u'修改' or u'创建') + u'内容: ' + unicode(obj) + u' 成功')
            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET.get('next'))
            return redirect('admin:cms:content-path', path.path)
    else:
        form = Form(instance=content)
    
    # 表单字段分离
    main_fields = []
    meta_fields = []
    meta_fields_name = ['is_hidden']
    _t = path.model_config.get('form_meta_fields')
    if _t:
        meta_fields_name.extend(_t)
    
    for i in form.visible_fields():
        if i.name in meta_fields_name:
            meta_fields.append(i)
        else:
            main_fields.append(i)
    
    return 'content_edit', locals()


@render
def content_edit(request, response, content_id=None):
    return _content_edit(request, response, content_id=content_id)


@render
@path_wrap
def content_create(request, response, current_path):
    return _content_edit(request, response, current_path=current_path)


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^/path$', path, name='path'),
    url(r'^/path/create$', path_edit, name='path-create'),
    url(r'^/path/(?P<path_id>\d+)$', path_edit, name='path-edit'),
    url(r'^/path/(?P<path_id>\d+)/delete$', path_delete, name='path-delete'),
    
    url(r'^/content$', content, name='content'),
    url(r'^/content/path/(?P<path>.*)$', content, name='content-path'),
    url(r'^/content/create/(?P<path>.*)$', content_create, name='content-create'),
    url(r'^/content/edit/(?P<content_id>\d+)$', content_edit, name='content-edit'),
    url(r'^/content/action$', content_action, name='content-action'),
    
    url(r'^/recycle$', recycle, name='recycle'),
    url(r'^/recycle/clear$', recycle_clear, name='recycle-clear'),
]

sub_menus = [
    ('admin:cms:content', u'内容管理', 'fa fa-edit'),
    ('admin:cms:path', u'栏目管理', 'fa fa-sitemap'),
    ('admin:cms:recycle', u'回收站', 'fa fa-trash'),
]

PERMISSIONS = {
    'path.edit': u'栏目|创建/编辑',
    'path.delete': u'栏目|删除',
    'recycle.fire': u'回收站|批量删除',
    'recycle.clear': u'回收站|清空',
    'content.create': u'内容|创建',
    'content.update.self': u'内容|修改本人内容',
    'content.update.other': u'内容|修改他人内容',
    'content.recover': u'内容|删除恢复',
}


# 批量操作权限
def _load_actions():
    for a, i in CONTENT_ACTIONS.items():
        perm = 'action.%s' % a
        PERMISSIONS[perm] = u'内容|%s' % i['name']
_load_actions()
