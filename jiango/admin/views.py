# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
from jiango.pagination import Paging
from .shortcuts import renderer, Alert, has_superuser
from .forms import AuthenticationForm, SetPasswordForm, UserForm
from .auth import LOGIN_NEXT_FIELD, set_login, set_login_cookie, set_logout, set_logout_cookie, get_request_user
from .config import SECRET_KEY_DIGEST
from .models import User, Log, get_password_digest


render = renderer('admin/')


@render
def index(request, response):
    online_set = set(User.objects.online())
    online_count = len(online_set)
    log_set = Log.objects.select_related('user')[:10]
    log_count = Log.objects.count()
    return locals()


@render(logout=True)
def login(request, response):
    secret_key = SECRET_KEY_DIGEST
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            next_url = request.REQUEST.get(LOGIN_NEXT_FIELD, reverse('admin:-index'))
            resp = HttpResponseRedirect(next_url)
            set_login(user)
            set_login_cookie(resp, user)
            Log.write(Log.SUCCESS, 'admin', u'用户 %s 登陆成功' % user.username, Log.LOGIN,
                      remote_ip=request.META.get('REMOTE_ADDR'), user=user)
            return resp
        Log.write(Log.WARNING, 'admin', u'尝试登陆\n用户名: %s\n\n%s' % (
                        form.data.get('username',''), form.errors.as_text()), Log.LOGIN,
                  remote_ip=request.META.get('REMOTE_ADDR'), user=form.get_user())
    else:
        form = AuthenticationForm()
    return locals()


# login=False 防止用户已经退出后再刷新此页，然后跳转到登陆页面，登陆完了又退出
@render(login=False)
def logout(request, response):
    user = get_request_user(request)
    if user:
        set_logout(user)
        Log.write(Log.SUCCESS, 'admin', u'用户 %s 退出成功' % user.username, Log.LOGOUT,
                  remote_ip=request.META.get('REMOTE_ADDR'), user=user)
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
            Log.write(Log.SUCCESS, 'admin', u'修改 %s 的登陆密码' % target_user, Log.UPDATE,
                      remote_ip=request.META.get('REMOTE_ADDR'), user=user)
            if user.pk == target_user.pk:
                set_login_cookie(response, user)
            raise Alert(Alert.SUCCESS, u'修改 %s 的登陆密码成功' % target_user,
                        {u'返回':reverse('admin:-index')}, back=False)
        
        Log.write(Log.WARNING, 'admin', u'修改 %s 的登陆密码失败\n\n%s' % (target_user, form.errors.as_text()),
                  Log.UPDATE, remote_ip=request.META.get('REMOTE_ADDR'), user=user)
        
        # 当前密码验证出错强制退出用户
        if form.current_password_error:
            set_logout(user)
            Log.write(Log.WARNING, 'admin', u'修改 %s 的登陆密码时验证当前密码错误被强制退出' % target_user, Log.LOGOUT,
                      remote_ip=request.META.get('REMOTE_ADDR'), user=user)
            set_logout_cookie(response)
            raise Alert(Alert.ERROR, u'修改登陆密码时验证当前密码错误被强制退出',
                        {u'重新登陆':reverse('admin:-login')}, back=False)
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


@render(perm='admin.user.view')
def user_show(request, response, user_id):
    user = User.objects.get(pk=user_id)
    return locals()


@render
def user_edit(request, response, user_id=None):
    has_superuser(request)
    user = User.objects.get(pk=user_id) if user_id else None
    action = Log.UPDATE if user else Log.CREATE
    action_name = u'编辑' if user else u'添加'
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            raw_password = None
            if not user:
                raw_password = get_random_string(6)
                form.instance.password_digest = get_password_digest(raw_password)
            user = form.save()
            Log.write(Log.SUCCESS, 'admin', u'%s %s 管理员' % (action_name, user), action,
                      view_name='admin:-user-show', view_args=(user.pk,),
                      remote_ip=request.META.get('REMOTE_ADDR'), user=get_request_user(request))
            raise Alert(Alert.SUCCESS, u'成功%s管理员%s' % (action_name, u'，登陆密码: %s' % raw_password if raw_password else ''),{
                    u'完成': reverse('admin:-user-list'),
                    u'查看': reverse('admin:-user-show', args=(user.pk,)),
                }, False)
        Log.write(Log.WARNING, 'admin', u'%s管理员失败\n\n%s' % (action_name, form.errors.as_text()),
                  action, remote_ip=request.META.get('REMOTE_ADDR'), user=get_request_user(request))
    else:
        form = UserForm(instance=user)
    return locals()
