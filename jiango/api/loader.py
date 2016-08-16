# -*- coding: utf-8 -*-
# Created on 2012-9-19
# @author: Yefei
from django.conf.urls import url, include
from jiango.importlib import autodiscover_installed_apps
from .shortcuts import formats, render


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


# 如果 output_format=None 则默认支持所有系统支持的格式，否则会增加 URL 后缀
def register(path, func, name=None, output_format=None):
    if output_format:
        u = url(r'^%s$' % path,
                render(func), kwargs = {'output_format':output_format}, name = name)
    else:
        u = url(r'^%s\.(?P<output_format>%s)$' % (path, '|'.join(formats)),
                render(func), name = name)
    urlpatterns.append(u)


def api(func_or_path=None, name=None):
    def wrapper(func):
        if func.__module__ not in loaded_apis:
            loaded_apis[func.__module__] = []
        loaded_apis[func.__module__].append((func, None if func_or_path == func else func_or_path, name))
        return func
    
    # @api() 带参数
    if func_or_path is None or isinstance(func_or_path, basestring):
        return wrapper
    
    # @api 不带参数
    return wrapper(func_or_path)


# 如果设置 output_format 则会省略 URL 后缀
def api_urls(namespace='api', module_name='api', output_format=None):
    autodiscover(module_name)
    
    for module, namesapces in loaded_modules.iteritems():
        for func, func_or_path, name in loaded_apis.get(module, []):
            if func_or_path and func_or_path.startswith('/'):
                path = func_or_path[1:]
            else:
                path = '/'.join(namesapces + [func_or_path or func.__name__])
            name = '-'.join(namesapces + [name or func.__name__])
            register(path, func, name, output_format)
    
    return include(urlpatterns, namespace)
