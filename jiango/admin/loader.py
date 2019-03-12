# -*- coding: utf-8 -*-
# Created on 2015-9-1
# @author: Yefei
from inspect import isfunction
from django.conf.urls import url, include
from django.utils.text import capfirst
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse, resolve
from django.shortcuts import redirect
from jiango.importlib import autodiscover_installed_apps


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


def index(request):
    return redirect('admin:admin:index')


urlpatterns = [
    url(r'^$', index, name='-index'),
]


def _get_sub_menus(request, current_view_name, sub_menus):
    menus = []
    for i in sub_menus:
        url_name = i[0]
        url_args = []
        url_kwargs = {}
        if isinstance(url_name, (tuple, list)):
            url_name, url_kwargs, url_active_key = i[0]
            is_active = getattr(request, 'admin_active_menu', '') == url_active_key
        else:
            # 菜单项匹配规则 aaa:bbb:ccc 完全相等 或者开头为  aaa:bbb:ccc- 用 - 分割子项
            is_active = current_view_name == url_name or current_view_name.startswith(url_name + '-')
        value = dict(
            url=reverse(url_name, args=url_args, kwargs=url_kwargs),
            is_active=is_active,
            verbose_name=url_name,
            icon=None,
            append=None,
        )
        l = len(i)
        if l > 1:
            value['verbose_name'] = i[1]
            if l > 2:
                value['icon'] = i[2]
                if l > 3:
                    value['append'] = i[3](request) if isfunction(i[3]) else i[3]
        menus.append(value)
    return menus


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
        sub_menus = _get_sub_menus(request, current_view_name, sub_menus)

        is_active = current_view_name.startswith('admin:%s:' % app_name)

        navigation.append(dict(url=reverse('admin:%s:index' % app_name),
                               app_name=app_name,
                               verbose_name=verbose_name,
                               icon=icon,
                               sub_menus=sub_menus,
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
