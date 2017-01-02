# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from functools import wraps
from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from jiango.shortcuts import render_to_string, HttpReload
from .auth import login_redirect, logout_redirect, get_request_user
from .models import Permission, Log, LogTypes


class Alert(Exception):
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    TAGS = {DEBUG: 'debug',
            INFO: 'info',
            SUCCESS: 'success',
            WARNING: 'warning',
            ERROR: 'error'}
    
    def __init__(self, level, message, buttons=None, back=True):
        self.level = level
        self.message = message
        self.buttons = buttons or {}
        self.back = back
    
    @property
    def tag(self):
        return self.TAGS[self.level]


def has_superuser(request):
    user = get_request_user(request)
    if user and user.is_active and user.is_superuser:
        return
    raise Alert(Alert.ERROR, u'只有超级用户才有权利操作')


def has_perm(request, codename):
    user = get_request_user(request)
    if user and user.has_perm(codename):
        return
    try:
        perm = Permission.objects.get(codename=codename)
        perm_name = perm.name
    except Permission.DoesNotExist:
        perm_name = codename
    raise Alert(Alert.ERROR, u'你没有 "%s" 权限' % perm_name)


def renderer(prefix=None, default_extends_layout=True,
             template_ext='html', content_type=settings.DEFAULT_CONTENT_TYPE):
    def render(func=None, extends_layout=default_extends_layout,
               login=True, logout=False, perm=None):
        def do_wrapper(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                response = HttpResponse(content_type=content_type)
                content = ''
                
                if logout:
                    if get_request_user(request):
                        return logout_redirect(request)
                elif login:
                    if not get_request_user(request):
                        return login_redirect(request)
                
                try:
                    if perm:
                        has_perm(request, perm)
                    result = func(request, response, *args, **kwargs)
                except HttpReload as e:
                    return e.response(request, response)
                except (Alert, ObjectDoesNotExist) as e:
                    result = {}
                    if isinstance(e, Alert):
                        result = {'message': e.message, 'tag': e.tag, 'buttons': e.buttons}
                        if e.back and 'HTTP_REFERER' in request.META:
                            result['buttons'][u'返回'] = request.META['HTTP_REFERER']
                    elif isinstance(e, ObjectDoesNotExist):
                        result = {'message': u'所访问的对象不存在，可能已经被删除。\n%s' % e, 'tag':'error'}
                    content = render_to_string(request, result, '/admin/alert', prefix, template_ext)
                else:
                    if isinstance(result, HttpResponse):
                        return result
                    content = render_to_string(request, result, func.__name__.rstrip('_'), prefix, template_ext)
                    if not extends_layout:
                        response.content = content
                        return response
                
                from .loader import get_navigation
                user = get_request_user(request)
                base_dictionary = {'content': content,
                                   'navigation': user and get_navigation(request),
                                   'sidebar_collapse': request.COOKIES.get('admin-sidebar-collapse') == '1',
                                   'user': user}
                response.content = render_to_string(request, base_dictionary, 'admin/layout')
                return response
            return wrapper
        
        # @render() 带参数
        if func is None:
            return do_wrapper
        
        # @render 不带参数
        return do_wrapper(func)
    return render


class Logger(LogTypes):
    def __init__(self, app_label):
        self.app_label = app_label
    
    def __call__(self, request, level, content, action=None, user=None, remote_ip=None,
                 view_name=None, view_args=None, view_kwargs=None, form=None):
        if form:
            content = '%s\n\n%s' % (content, form.errors.as_text())
        
        if action is None:
            action = LogTypes.NONE
        
        if remote_ip is None:
            remote_ip = request.META.get('REMOTE_ADDR')
        
        if user is None:
            user = get_request_user(request)
        
        return Log.write(level, self.app_label, content, action,
                         view_name, view_args, view_kwargs, remote_ip, user)
    
    def debug(self, request, content, *args, **kwargs):
        return self(request, LogTypes.DEBUG, content, *args, **kwargs)
    
    def info(self, request, content, *args, **kwargs):
        return self(request, LogTypes.INFO, content, *args, **kwargs)
    
    def success(self, request, content, *args, **kwargs):
        return self(request, LogTypes.SUCCESS, content, *args, **kwargs)
    
    def warning(self, request, content, *args, **kwargs):
        return self(request, LogTypes.WARNING, content, *args, **kwargs)
    
    def error(self, request, content, *args, **kwargs):
        return self(request, LogTypes.ERROR, content, *args, **kwargs)


class ModelLogger(object):
    def __init__(self, instance=None):
        self.instance_values = None
        self.instance_class_name = None
        self.instance_verbose_name = None
        if instance:
            self.instance_values = self.get_instance_values(instance)
            self.instance_class_name = str(instance.__class__)
            self.instance_verbose_name = instance._meta.verbose_name

    @staticmethod
    def get_instance_values(instance):
        return [(f.attname, unicode(getattr(instance, f.attname))) for f in instance._meta.local_fields]
    
    def diff_values(self, new_instance):
        if not self.instance_values:
            return False
        diff_values = []
        for attname, orig_value in self.instance_values:
            new_value = unicode(getattr(new_instance, attname))
            if new_value != orig_value:
                diff_values.append((attname, orig_value, new_value))
        return diff_values
    
    def message(self, new_instance=None):
        if not self.instance_values and not new_instance:
            return ''
        if not self.instance_values:
            self.instance_class_name = str(new_instance.__class__)
            self.instance_verbose_name = new_instance._meta.verbose_name
        
        output = [u'模型: ' + self.instance_class_name, u'名称: ' + self.instance_verbose_name]
        
        if not self.instance_values:
            # 新增类型，无需记录差异数据
            pass
        elif not new_instance:
            # 数据被删除
            output.append(u'删除之前的数据为:')
            for attname, orig_value in self.instance_values:
                output.append(attname + ': ' + orig_value)
        else:
            # 数据被更新
            diff_values = self.diff_values(new_instance)
            if not diff_values:
                output.append(u'没有变化')
            else:
                output.append(u'更新字段:')
                for attname, orig_value, new_value in diff_values:
                    output.append(attname + ': ' + orig_value + ' > ' + new_value)
        return '\n'.join(output)
