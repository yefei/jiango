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


urlpatterns = [
    url(r'^$', views.index, name='-index'),
    url(r'^-/login$', views.login, name='-login'),
    url(r'^-/logout$', views.logout, name='-logout'),
    url(r'^-/password$', views.set_password, name='-password'),
    
    url(r'^-/log$', views.log_list, name='-log'),
    url(r'^-/log/(?P<log_id>\d+)$', views.log_show, name='-log-show'),
    
    url(r'^-/user$', views.user_list, name='-user'),
    url(r'^-/user/add$', views.user_edit, name='-user-add'),
    url(r'^-/user/(?P<user_id>\d+)$', views.user_show, name='-user-show'),
    url(r'^-/user/(?P<user_id>\d+)/edit$', views.user_edit, name='-user-edit'),
    url(r'^-/user/(?P<user_id>\d+)/password$', views.set_password, name='-user-password'),
    url(r'^-/user/(?P<user_id>\d+)/delete$', views.user_delete, name='-user-delete'),
    
    url(r'^-/group$', views.group_list, name='-group'),
    url(r'^-/group/add$', views.group_edit, name='-group-add'),
    url(r'^-/group/(?P<group_id>\d+)$', views.group_show, name='-group-show'),
    url(r'^-/group/(?P<group_id>\d+)/edit$', views.group_edit, name='-group-edit'),
    url(r'^-/group/(?P<group_id>\d+)/delete$', views.group_delete, name='-group-delete'),
]

system_sub_menus = [
    # url_name, name, icon
    ('admin:-index', u'系统首页', 'fa fa-dashboard'),
    ('admin:-log', u'系统日志', 'fa fa-file-text-o'),
    ('admin:-user', u'管理员', 'fa fa-user'),
    ('admin:-group', u'管理组', 'fa fa-group'),
    ('admin:-password', u'修改密码', 'fa fa-lock'),
]


def _get_sub_menus(current_view_name, sub_menus):
    return [dict(url=reverse(_url),
                 verbose_name=_name,
                 icon=_icon,
                 is_active=current_view_name.startswith(_url)) for _url, _name, _icon in sub_menus]


def get_navigation(request):
    navigation = []
    current_view_name = resolve(request.path).view_name
    for module, app_name in loaded_modules.iteritems():
        icon = getattr(module, 'icon', None)
        icon = icon(request) if isfunction(icon) else icon

        verbose_name = getattr(module, 'verbose_name', capfirst(app_name))
        verbose_name = verbose_name(request) if isfunction(verbose_name) else verbose_name
        if not verbose_name:
            continue

        sub_menus = getattr(module, 'sub_menus', [])
        sub_menus = sub_menus(request) if isfunction(sub_menus) else sub_menus
        sub_menus = _get_sub_menus(current_view_name, sub_menus)

        is_active = current_view_name.startswith('admin:%s' % app_name)

        navigation.append(dict(url=reverse('admin:%s:index' % app_name),
                               verbose_name=verbose_name,
                               icon=icon,
                               sub_menus=sub_menus,
                               is_active=is_active))

    navigation.append(dict(url=reverse('admin:-index'),
                           verbose_name=u'系统',
                           icon=None,
                           sub_menus=_get_sub_menus(current_view_name, system_sub_menus),
                           is_active=current_view_name.startswith('admin:-')))
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
