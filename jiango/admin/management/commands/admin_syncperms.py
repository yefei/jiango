# -*- coding: utf-8 -*-
# Created on 2015-9-5
# @author: Yefei
from inspect import isfunction
from django.core.management.base import BaseCommand
from django.utils.importlib import import_module
from django.utils.text import capfirst
from django.utils.datastructures import SortedDict
from jiango.admin.models import Permission
from jiango.admin.config import ADMIN_PERMISSIONS


class Command(BaseCommand):
    help = 'Used to sync admin apps permissions.'
    
    def handle(self, *args, **options):
        # 触发 admin.loader
        from django.conf import settings
        import_module(settings.ROOT_URLCONF)
        
        from jiango.admin.loader import loaded_modules
        
        perms = SortedDict([('admin.' + codename, u'管理系统|' + name) for codename, name in ADMIN_PERMISSIONS.items()])
        
        for module, app_label in loaded_modules.items():
            app_perms = getattr(module, 'PERMISSIONS', {})
            verbose_name = getattr(module, 'verbose_name', capfirst(app_label))
            if isfunction(verbose_name):
                verbose_name = verbose_name(None)
            for codename, name in app_perms.items():
                perms['.'.join((app_label, codename))] = '|'.join((verbose_name, name))
        
        # 更新删除检查
        for i in Permission.objects.all():
            # 已存在的
            if i.codename in perms:
                # 更新检查
                if perms[i.codename] != i.name:
                    print >>self.stdout, 'rename', i.codename + ':', i.name, '>', perms[i.codename]
                    i.name = perms[i.codename]
                    i.save()
                del perms[i.codename]
            # 不存在的
            else:
                # 删除询问
                while 1:
                    raw_value = raw_input(i.codename + ': Has not been used to delete? (y/n)')
                    if raw_value.lower() == 'y':
                        i.delete()
                        break
                    if raw_value.lower() == 'n':
                        break
        
        # 同步到数据库
        for codename, name in perms.items():
            print >>self.stdout, 'install', codename + ':', name
            Permission.objects.create(codename=codename, name=name)
        
        self.stdout.write("Sync permissions successfully.\n")
