# -*- coding: utf-8 -*-
# Created on 2015-9-1
# @author: Yefei
from django.conf.urls import url, include
from jiango.importlib import autodiscover_installed_apps
from . import views


# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False
loaded_modules = {}


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
]


def autodiscover(module_name):
    global LOADING
    if LOADING:
        return
    LOADING = True
    for namesapce, module in autodiscover_installed_apps(module_name):
        loaded_modules[module] = namesapce
    # autodiscover was successful, reset loading flag.
    LOADING = False


def admin_urls(module_name='admin'):
    autodiscover(module_name)
    for module, app_name in loaded_modules.iteritems():
        urlpatterns.append(url(r'^%s/' % app_name, include(module.urlpatterns, app_name)))
    return include(urlpatterns, 'admin')
