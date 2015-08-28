# -*- coding: utf-8 -*-
# Created on 2012-9-19
# @author: Yefei
import sys
from functools import wraps
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from jiango.importlib import autodiscover_installed_apps
from jiango.serializers import get_public_serializer_formats, get_serializer, deserialize
from .utils import Param
from .exceptions import APIError, LoginRequerd, Deny


# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False
urlpatterns = []

def autodiscover():
    global LOADING
    if LOADING:
        return
    LOADING = True
    autodiscover_installed_apps('apis', True)
    # autodiscover was successful, reset loading flag.
    LOADING = False


formats = get_public_serializer_formats()
content_types = dict([(get_serializer(f).content_type, f) for f in formats])


def render(func):
    @wraps(func)
    def wrapper(request, output_format, *args, **kwargs):
        status = 200
        serializer = get_serializer(output_format)()
        response = HttpResponse(content_type=serializer.content_type)
        
        try:
            user = getattr(request, 'user')
            if func.login_requerd and not user:
                raise LoginRequerd
            if func.admin_requerd and not user.is_admin:
                raise Deny('Admin requerd!')
            
            request.param = Param(request.REQUEST)
            request.value = None
            content_type = request.META.get('CONTENT_TYPE')
            if content_type in content_types and request.body:
                try:
                    request.value = deserialize(content_types[content_type], request.body)
                except Exception, e:
                    raise APIError(e.message)
            
            value = func(request, response, *args, **kwargs)
            
        except (APIError, ObjectDoesNotExist), e:
            value = {'type':e.__class__.__name__, 'message':e.message}
            status = e.status_code if hasattr(e, 'status_code') else 422
        
        response.content = serializer.serialize(value)
        response.status_code = status
        return response
    return wrapper


def register(path, func, name=None):
    global urlpatterns
    urlpatterns.append(url(r'^%s\.(?P<output_format>%s)$' % (path, '|'.join(formats)),
                           render(func),
                           name = name if name else path.strip('/').replace('/', '-')))


def get_func_app_ns(func):
    return sys.modules[func.__module__].__name__.split('.')[1:-1]


def api(func_or_path=None, name=None, login_requerd=False, admin_requerd=False):
    def wrapper(func):
        path = func_or_path
        func.login_requerd = login_requerd or admin_requerd
        func.admin_requerd = admin_requerd
        ns = get_func_app_ns(func)
        # @api(login_requerd=True)
        if path is None:
            path = '/'.join(ns + ([] if func.__name__ == 'index' else [func.__name__]))
        # @api('/root/urlpath')
        elif path.startswith('/'):
            path = path[1:]
        else:
            path = '/'.join(ns + [path])
        _name = '-'.join(ns + [name]) if name else None
        register(path, func, _name)
        return func
    
    # @api('sub/urlpath') or @api('/root/urlpath') or @api(r'(\d+)')
    # @api(name='other') or @api(login_requerd=True)
    if func_or_path is None or isinstance(func_or_path, basestring):
        return wrapper
    
    # @api
    func_or_path.login_requerd = login_requerd or admin_requerd
    func_or_path.admin_requerd = admin_requerd
    ns = get_func_app_ns(func_or_path)
    funcname = func_or_path.__name__
    path = '/'.join(ns + ([] if funcname == 'index' else [funcname]))
    register(path, func_or_path, '-'.join(ns + [funcname]))
    
    return func_or_path
