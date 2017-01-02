# -*- coding: utf-8 -*-
# Created on 2015-9-1
# @author: Yefei
from inspect import isfunction
from django.conf.urls import url, include
from django.utils.text import capfirst
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse, resolve
from jiango.importlib import autodiscover_installed_apps
from . import views


# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False
loaded_modules = SortedDict()


urlpatterns = [
    url(r'^$', views.index, name='-index'),
    url(r'^-/login$', views.login, name='-login'),
    url(r'^-/logout$', views.logout, name='-logout'),
    url(r'^-/password$', views.set_password, name='-password'),
    
    url(r'^-/log$', views.log_list, name='-log-list'),
    url(r'^-/log/(?P<log_id>\d+)$', views.log_show, name='-log-show'),
    
    url(r'^-/user$', views.user_list, name='-user-list'),
    url(r'^-/user/add$', views.user_edit, name='-user-add'),
    url(r'^-/user/(?P<user_id>\d+)$', views.user_show, name='-user-show'),
    url(r'^-/user/(?P<user_id>\d+)/edit$', views.user_edit, name='-user-edit'),
    url(r'^-/user/(?P<user_id>\d+)/password$', views.set_password, name='-user-password'),
    url(r'^-/user/(?P<user_id>\d+)/delete$', views.user_delete, name='-user-delete'),
    
    url(r'^-/group$', views.group_list, name='-group-list'),
    url(r'^-/group/add$', views.group_edit, name='-group-add'),
    url(r'^-/group/(?P<group_id>\d+)$', views.group_show, name='-group-show'),
    url(r'^-/group/(?P<group_id>\d+)/edit$', views.group_edit, name='-group-edit'),
    url(r'^-/group/(?P<group_id>\d+)/delete$', views.group_delete, name='-group-delete'),
]


def autodiscover(module_name):
    global LOADING
    if LOADING:
        return
    LOADING = True
    for namesapce, module in autodiscover_installed_apps(module_name):
        if hasattr(module, 'urlpatterns'):
            loaded_modules[module] = namesapce
    # autodiscover was successful, reset loading flag.
    LOADING = False


def get_navigation(request):
    navigation = []
    for module, app_name in loaded_modules.iteritems():
        icon = getattr(module, 'icon', None)
        icon = icon(request) if isfunction(icon) else icon
        verbose_name = getattr(module, 'verbose_name', capfirst(app_name))
        verbose_name = verbose_name(request) if isfunction(verbose_name) else verbose_name
        if not verbose_name:
            continue
        resolver_match = resolve(request.path)
        is_active = resolver_match.view_name.startswith('admin:' + app_name)
        navigation.append(dict(url=reverse('admin:%s:index' % app_name),
                               verbose_name=verbose_name,
                               icon=icon,
                               is_active=is_active))
    return navigation


def get_app_verbose_name(app_name):
    for module, _app_name in loaded_modules.iteritems():
        if app_name == _app_name:
            verbose_name = getattr(module, 'verbose_name', capfirst(app_name))
            if isfunction(verbose_name):
                verbose_name = verbose_name(None)
            return verbose_name
    return capfirst(app_name)


def admin_urls(module_name='admin'):
    autodiscover(module_name)
    for module, app_name in loaded_modules.iteritems():
        urlpatterns.append(url(r'^%s' % app_name, include(module.urlpatterns, app_name)))
    return include(urlpatterns, 'admin')
