# -*- coding: utf-8 -*-
# Created on 2015-10-13
# @author: Yefei
"""
from jiango.cms.urls import urlpatterns as cms_urls

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin_urls()),
    url(r'^api/captcha/', include('jiango.captcha.urls')),
    url(r'^api/', api_urls()),
    *cms_urls # root include
)
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<path>.*)/page.(?P<page>\d+)/$', views.content_list, name='cms-list'),
    url(r'^(?P<path>.*)/(?P<content_id>\d+)/$', views.content_show, name='cms-content'),
    url(r'^(?P<path>.*)/$', views.column, name='cms-column'),
]
