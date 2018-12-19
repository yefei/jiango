# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2018/12/19
from django.conf import settings


def get_setting(name, default=None):
    return getattr(settings, 'JIANGO_%s' % name, default)
