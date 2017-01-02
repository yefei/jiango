# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.shortcuts import redirect
from django.contrib import messages
from jiango.pagination import Paging
from .shortcuts import renderer, Alert, has_superuser, has_perm, Logger
from .forms import AuthenticationForm, SetPasswordForm, UserForm, GroupForm
from .auth import LOGIN_NEXT_FIELD, set_login, set_login_cookie, set_logout, set_logout_cookie, get_request_user
from .config import SECRET_KEY_DIGEST
from .models import User, Log, get_password_digest, Group


render = renderer('admin/')
log = Logger('admin')


@render
def index(request, response):
    online_set = set(User.objects.online())
    online_count = len(online_set)
    log_set = Log.objects.select_related('user')[:10]
    log_count = Log.objects.count()
    return locals()


@render(logout=True, extends_layout=False)
def login(request, response):
    secret_key = SECRET_KEY_DIGEST
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                log(request, log.WARNING, u'用户 %s 认证成功，由于账户已被停用而被禁止登陆' % user.username, log.LOGIN, user=user)
                raise Alert(Alert.ERROR, u'您的帐号已经被停用')
            next_url = request.REQUEST.get(LOGIN_NEXT_FIELD, reverse('admin:-index'))
            resp = HttpResponseRedirect(next_url)
            set_login(user)
            set_login_cookie(resp, user)
            log(request, log.SUCCESS, u'用户 %s 登陆成功' % user.username, log.LOGIN, user=user)
            return resp
        log(request, log.WARNING, u'尝试登陆\n用户名: %s' % form.data.get('username',''),
            log.LOGIN, user=form.get_user(), form=form)
    else:
        form = AuthenticationForm()
    return locals()


# login=False 防止用户已经退出后再刷新此页，然后跳转到登陆页面，登陆完了又退出
@render(login=False, extends_layout=False)
def logout(request, response):
    user = get_request_user(request)
    if user:
        set_logout(user)
        log(request, log.SUCCESS, u'用户 %s 退出' % user.username, log.LOGOUT)
    set_logout_cookie(response)


@render
def set_password(request, response, user_id=None):
    secret_key = SECRET_KEY_DIGEST
    user = get_request_user(request)
    target_user = User.objects.get(pk=user_id) if user_id else user
    
    # 修改他人密码
    if user.pk != target_user.pk:
        has_superuser(request)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            target_user.update_password(form.cleaned_data['new'])
            log(request, log.SUCCESS, u'修改 %s 的登陆密码' % target_user, log.UPDATE)
            messages.success(request, u'成功修改 %s 的登陆密码' % target_user)
            resp = redirect('admin:-index')
            if user.pk == target_user.pk:
                set_login_cookie(resp, user)
            return resp
        
        log(request, log.WARNING, u'修改 %s 的登陆密码' % target_user, log.UPDATE, form=form)
        
        # 当前密码验证出错强制退出用户
        if form.current_password_error:
            set_logout(user)
            log(request, log.WARNING, u'修改 %s 的登陆密码时验证当前密码错误被强制退出' % target_user, log.LOGOUT)
            set_logout_cookie(response)
            raise Alert(Alert.ERROR, u'修改登陆密码时验证当前密码错误被强制退出',
                        {u'重新登陆': reverse('admin:-login')}, back=False)
    else:
        form = SetPasswordForm(user)
    return locals()


@render(perm='admin.log.view')
def log_list(request, response):
    log_set = Log.objects.select_related('user')
    log_set = Paging(log_set, request).page()
    return locals()


@render(perm='admin.log.view')
def log_show(request, response, log_id):
    result = Log.objects.get(pk=log_id)
    return locals()


@render(perm='admin.user.view')
def user_list(request, response):
    user_set = User.objects.all()
    user_set = Paging(user_set, request).page()
    return locals()


@render
def user_show(request, response, user_id):
    user = User.objects.get(pk=user_id)
    if get_request_user(request) != user:
        has_perm(request, 'admin.user.view')
    return locals()


@render
def user_edit(request, response, user_id=None):
    has_superuser(request)
    user = User.objects.get(pk=user_id) if user_id else None
    action = log.UPDATE if user else log.CREATE
    action_name = u'编辑' if user else u'添加'
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            raw_password = None
            if not user:
                raw_password = get_random_string(6)
                form.instance.password_digest = get_password_digest(raw_password)
            user = form.save()
            log(request, log.SUCCESS, u'%s管理员: %s' % (action_name, user), action,
                view_name='admin:-user-show', view_args=(user.pk,), form=form)
            messages.success(request,
                             u'成功%s管理员%s' % (action_name, (u'，初始密码: %s' % raw_password) if raw_password else ''),
                             'sticky' if raw_password else '')
            return redirect('admin:-user-show', user.pk)
        log(request, log.ERROR, u'%s管理员失败' % action_name, action, form=form)
    else:
        form = UserForm(instance=user)
    return locals()


@render
def user_delete(request, response, user_id):
    has_superuser(request)
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        log(request, log.SUCCESS, u'删除用户: %s' % user, log.DELETE)
        messages.success(request, u'删除完成')
        user.delete()
        return redirect('admin:-user-list')
    return locals()


@render(perm='admin.group.view')
def group_list(request, response):
    group_set = Group.objects.prefetch_related('permissions')
    return locals()


@render(perm='admin.group.view')
def group_show(request, response, group_id):
    group = Group.objects.get(pk=group_id)
    return locals()


@render
def group_edit(request, response, group_id=None):
    has_superuser(request)
    group = Group.objects.get(pk=group_id) if group_id else None
    action = log.UPDATE if group else log.CREATE
    action_name = u'编辑' if group else u'添加'
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            log(request, log.SUCCESS, u'%s %s 用户组' % (action_name, group), action,
                view_name='admin:-group-show', view_args=(group.pk,), form=form)
            messages.success(request, u'成功%s用户组' % action_name)
            return redirect('admin:-group-show', group.pk)
        log(request, log.ERROR, u'%s用户组失败' % action_name, action, form=form)
    else:
        form = GroupForm(instance=group)
    return locals()


@render
def group_delete(request, response, group_id):
    has_superuser(request)
    group = Group.objects.get(pk=group_id)
    if request.method == 'POST':
        log(request, log.SUCCESS, u'删除用户组: %s' % group, log.DELETE)
        messages.success(request, u'删除完成')
        group.delete()
        return redirect('admin:-group-list')
    return locals()
