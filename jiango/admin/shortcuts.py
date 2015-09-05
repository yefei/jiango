# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from functools import wraps
from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from jiango.shortcuts import render_to_string
from .auth import login_required, logout_required, get_request_user
from .models import Permission


class Alert(Exception):
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    TAGS = {DEBUG:'debug',
            INFO:'info',
            SUCCESS:'success',
            WARNING:'warning',
            ERROR:'error'}
    
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
    raise Alert(Alert.ERROR, u'你没有%s权限' % perm_name)


def renderer(prefix=None, default_extends_layout=True,
             template_ext='html', content_type=settings.DEFAULT_CONTENT_TYPE):
    
    def render(func=None, extends_layout=default_extends_layout,
               login=True, logout=False, perm=None):
        def do_wrapper(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                response = HttpResponse(content_type=content_type)
                
                if logout:
                    _func = logout_required(func)
                elif login:
                    _func = login_required(func)
                else:
                    _func = func
                
                try:
                    if perm:
                        has_perm(request, perm)
                    result = _func(request, response, *args, **kwargs)
                except (Alert, ObjectDoesNotExist) as e:
                    result = {}
                    if isinstance(e, Alert):
                        result = {'message':e.message, 'tag':e.tag, 'buttons':e.buttons}
                        if e.back and 'HTTP_REFERER' in request.META:
                            result['buttons'][u'返回'] = request.META['HTTP_REFERER']
                    elif isinstance(e, ObjectDoesNotExist):
                        result = {'message':u'所访问的对象不存在，可能已经被删除。\n%s' % e, 'tag':'error'}
                    content = render_to_string(request, result, '/admin/alert', prefix, template_ext)
                else:
                    if isinstance(result, HttpResponse):
                        return result
                    content = render_to_string(request, result, func.__name__, prefix, template_ext)
                    if not extends_layout:
                        response.content = content
                        return response
                
                from .loader import get_navigation
                user = get_request_user(request)
                base_dictionary = {'content':content,
                                   'navigation': user and get_navigation(request),
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
