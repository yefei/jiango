# -*- coding: utf-8 -*-
# Created on 2012-9-20
# @author: Yefei
from django.core.management.base import BaseCommand
from django.utils.importlib import import_module


class Command(BaseCommand):
    help = "Show complete Django url configuration."
    
    def handle(self, *args, **options):
        from django.conf import settings
        urlconf = import_module(settings.ROOT_URLCONF)
        
        self._max_url_len = 0
        self._max_name_len = 0
        
        urls = []
        
        def _foreach_urls(urllist, depth=0, ns_depth=0):
            
            for entry in urllist:
                url = '  ' * depth + entry.regex.pattern
                self._max_url_len = max(len(url), self._max_url_len)
                
                name = ''
                d = 0
                if hasattr(entry, 'namespace') and entry.namespace:
                    name = entry.namespace
                    d = 1
                elif hasattr(entry, 'name') and entry.name:
                    name = entry.name
                
                name = '  ' * ns_depth + name
                self._max_name_len = max(len(name), self._max_name_len)
                
                urls.append((url, name))
                
                if hasattr(entry, 'url_patterns'):
                    _foreach_urls(entry.url_patterns, depth + 1, ns_depth + d)
        
        _foreach_urls(urlconf.urlpatterns)
        
        print "URL", ' ' * (self._max_url_len - 3), ' Name'
        print '-' * self._max_url_len, ' ', '-' * self._max_name_len
        
        for url, name in urls:
            print url, ' ' * (self._max_url_len - len(url)), ' ', name
