# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2018/12/19
from django.conf.urls import url
from .views import thumb
from .settings import THUMB_PREFIX

urlpatterns = [
    url(r'^%s/(?P<width>\d+)x(?P<height>\d+)/(?P<sign>[0-9a-fA-F]{32})/(?P<path>.*)$' % THUMB_PREFIX, thumb, name='thumb'),
]
