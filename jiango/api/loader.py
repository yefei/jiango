# -*- coding: utf-8 -*-
# Created on 2012-9-19
# @author: Yefei
from functools import wraps
from django.conf.urls import url, include
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from jiango.importlib import autodiscover_installed_apps
from jiango.serializers import get_public_serializer_formats, get_serializer, deserialize
from .utils import Param
from .exceptions import APIError


formats = get_public_serializer_formats()
content_types = dict([(get_serializer(f).content_type, f) for f in formats])

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False
loaded_apis = {}
loaded_modules = {}
urlpatterns = []


def autodiscover(module_name):
    global LOADING
    if LOADING:
        return
    LOADING = True
    for namesapces, module in autodiscover_installed_apps(module_name, True):
        loaded_modules[module.__name__] = namesapces
    # autodiscover was successful, reset loading flag.
    LOADING = False


def render(func):
    @wraps(func)
    def wrapper(request, output_format, *args, **kwargs):
        status = 200
        serializer = get_serializer(output_format)()
        response = HttpResponse(content_type=serializer.content_type)
        
        try:
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
    urlpatterns.append(url(r'^%s\.(?P<output_format>%s)$' % (path, '|'.join(formats)), render(func), name=name))


def api(func_or_path=None, name=None):
    def wrapper(func):
        if func.__module__ not in loaded_apis:
            loaded_apis[func.__module__] = []
        loaded_apis[func.__module__].append((func, None if func_or_path==func else func_or_path, name))
        return func
    
    # @api() 带参数
    if func_or_path is None or isinstance(func_or_path, basestring):
        return wrapper
    
    # @api 不带参数
    return wrapper(func_or_path)


def api_urls(namespace='api', module_name='api'):
    autodiscover(module_name)
    
    for module, namesapces in loaded_modules.iteritems():
        for func, func_or_path, name in loaded_apis.get(module, []):
            if func_or_path and func_or_path.startswith('/'):
                path = func_or_path
            else:
                path = '/'.join(namesapces + [func_or_path or func.__name__])
            name = '-'.join(namesapces + [name or func.__name__])
            register(path, func, name)
    
    return include(urlpatterns, namespace)
