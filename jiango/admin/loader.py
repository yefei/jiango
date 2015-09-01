# -*- coding: utf-8 -*-
# Created on 2015-9-1
# @author: Yefei
from django.utils.datastructures import SortedDict
from jiango.importlib import autodiscover_installed_apps


registered = SortedDict()

LOADING = False

# 自动根据 settings.INSTALLED_APPS 中的顺序查找所有 admin package 并注册
def autodiscover():
    global LOADING
    if LOADING: return
    LOADING = True
    imported_modules = autodiscover_installed_apps('admin')
    for app_label, module in imported_modules:
        register_admin(app_label, module)
    LOADING = False


# 注册 admin 包
def register_admin(app_label, module):
    global registered
    
    if getattr(module, '__NOT_JIANGO_ADMIN__', False):
        return False
    
    print app_label, module
    
    return True
