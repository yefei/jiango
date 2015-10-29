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


def register(path, func, name=None):
    urlpatterns.append(url(r'^%s\.(?P<output_format>%s)$' % (path, '|'.join(formats)), render(func), name=name))


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
