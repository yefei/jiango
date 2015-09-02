# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
from functools import wraps
from django.http import HttpResponse
from django.conf import settings
from jiango.shortcuts import render_to_string
from .auth import login_required, logout_required, get_admin_user


def renderer(prefix=None, default_extends_layout=True,
             template_ext='html', content_type=settings.DEFAULT_CONTENT_TYPE):
    
    def render(func=None, extends_layout=default_extends_layout, login=True, logout=False):
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
                    result = _func(request, response, *args, **kwargs)
                except Exception, e:
                    raise
                
                if isinstance(result, HttpResponse):
                    return result
                
                content = render_to_string(request, result, func.__name__, prefix, template_ext)
                
                if not extends_layout:
                    response.content = content
                    return response
                
                base_dictionary = {'content':content, 'user':get_admin_user(request)}
                response.content = render_to_string(request, base_dictionary, 'admin/layout')
                return response
            return wrapper
        
        # @render() 带参数
        if func is None:
            return do_wrapper
        
        # @render 不带参数
        return do_wrapper(func)
    return render
