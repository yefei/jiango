# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/24
"""
from jiango.admin.shortcuts import CURDAdmin
from jiango.admin.config import ADMIN_PERMISSIONS
from jiango.admin.admin import urlpatterns as system_urlpatterns, sub_menus as system_sub_menus
from .models import Auth


curd_admin = CURDAdmin(
    app_label='admin',
    name='wechat_auth',
    verbose_name=u'微信用户授权',
    model_class=Auth,
    display_fields=['id', 'openid', 'access_expired_at', 'refresh_expired_at', 'scope', 'created_at', 'updated_at'],
    search_fields=['openid'],
)

system_urlpatterns.extend(curd_admin.urlpatterns)

system_sub_menus.extend([
    ('admin:admin:wechat_auth', curd_admin.verbose_name, 'fa fa-wechat'),
])

ADMIN_PERMISSIONS.update(curd_admin.permissions)
