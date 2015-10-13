# -*- coding: utf-8 -*-
# Created on 2014-8-18
# @author: Yefei
from django.utils.importlib import import_module


def autodiscover_installed_apps(module_name, recursion_package=False):
    import imp, os
    from django.conf import settings
    
    imported_modules = []

    def _find(app, namespaces):
        mod = import_module(app)
        try:
            imported_modules.append((namespaces, import_module("%s.%s" % (app, module_name))))
        except ImportError:
            pass
        
        if recursion_package:
            try:
                app_path = mod.__path__
            except AttributeError:
                return
            for f in os.listdir(app_path[0]):
                f = os.path.join(app_path[0], f)
                if os.path.isdir(f):
                    try:
                        imp.find_module(module_name, [f])
                    except ImportError:
                        continue
                    package_name = os.path.basename(f)
                    _find("%s.%s" % (app, package_name), namespaces + [package_name])
    
    for app in settings.INSTALLED_APPS:
        app_label = app.split('.')[-1]
        _find(app, recursion_package and [app_label] or app_label)
    
    return imported_modules


def import_object(path):
    mod_path, cls_name = path.rsplit('.', 1)
    mod = import_module(mod_path)
    return getattr(mod, cls_name)
