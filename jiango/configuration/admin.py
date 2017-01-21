# -*- coding: utf-8 -*-
"""
Created on 2017/1/21
@author: Fei Ye <316606233@qq.com>
"""
from django.conf.urls import url
from django.conf import settings
from django.forms.fields import Field
from django.contrib import messages
from django.shortcuts import redirect
from jiango.admin.shortcuts import renderer, Alert, Logger
from jiango.admin.config import ADMIN_PERMISSIONS
from jiango.admin.loader import urlpatterns as system_urlpatterns, system_sub_menus
from .models import get_config_value, get_config_item, set_config_value
from .forms import ItemForm


render = renderer('admin/configuration/')
log = Logger('admin')


@render(perm='admin.config.view')
def index(request, response):
    items = []
    for i in getattr(settings, 'CONFIGURATION_ITEMS', []):
        key = i[0]
        verbose_name = (i[2].label if isinstance(i[2], Field) else i[2]) if len(i) > 2 else key
        value = get_config_value(key)
        items.append(dict(key=key, value=value, verbose_name=verbose_name))
    return locals()


@render(perm='admin.config.edit')
def edit(request, response, key):
    item = get_config_item(key)
    if item is None:
        raise Alert(Alert.ERROR, u'不存在的配置项: %s' % key)
    verbose_name = (item[2].label if isinstance(item[2], Field) else item[2]) if len(item) > 2 else key
    value = get_config_value(key)
    form = ItemForm(item, request.POST or None, initial={'value': value})
    if form.is_valid():
        log_content = u'修改配置项: %s(%s)' % (verbose_name, key)
        log_content += u'\n\n原值: %r\n新值: %r' % (value, form.cleaned_data['value'])
        log(request, log.SUCCESS, log_content, view_name='admin:-config-edit', view_args=[key])
        set_config_value(key, form.cleaned_data['value'])
        messages.success(request, u'成功修改配置项')
        return redirect('admin:-config')
    return locals()


system_urlpatterns.extend([
    url(r'^-/config$', index, name='-config'),
    url(r'^-/config/(?P<key>.+)$', edit, name='-config-edit'),
])

system_sub_menus.extend([
    ('admin:-config', u'系统配置', 'fa fa-cog'),
])

ADMIN_PERMISSIONS['config.view'] = u'查看系统配置'
ADMIN_PERMISSIONS['config.edit'] = u'修改系统配置'
