# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2018/12/19
from django.conf import settings


UNSET_TYPE = object()


# 取得一个配置项，没有返回 default
def get_setting(name, default=None):
    value = getattr(settings, 'JIANGO_%s' % name, default)
    # 配置项可以是一个函数，需要时再调用
    if callable(value):
        return value()
    return value


# 取得一个必须配置项，如果没有则抛出异常
def get_required_setting(name):
    value = get_setting(name, UNSET_TYPE)
    if value is UNSET_TYPE:
        raise Exception('required setting: JIANGO_%s' % name)
    return value


# 配置项统一加前缀
class PrefixSetting(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def get_setting(self, name, default=None):
        return get_setting(self.prefix + name, default)

    def get_required_setting(self, name):
        return get_required_setting(self.prefix + name)
