# -*- coding: utf-8 -*-
# @author: Fei Ye <316606233@qq.com>
from django.conf.urls import patterns, url
from django.conf import settings
from . import views

urlpatterns = patterns(
    '',
    url(r'^callback$', views.callback, name='jiango-wechat-callback'),
    url(r'^auth/redirect$', views.auth_redirect, name='jiango-wechat-auth-redirect'),
    url(r'^auth/callback$', views.auth_callback, name='jiango-wechat-auth-callback'),
)

if settings.DEBUG:
    urlpatterns.append(url(r'^auth/test$', views.auth_test))
