# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
import hashlib
from django.conf import settings


SECRET_KEY_DIGEST = hashlib.md5(settings.SECRET_KEY).hexdigest()

# 身份验证 cookie 名称
COOKIE_NAME = getattr(settings, 'ADMIN_COOKIE_NAME', 'jiango_admin_auth')

# 登陆跳转字段名称
LOGIN_NEXT_FIELD = getattr(settings, 'ADMIN_LOGIN_NEXT_FIELD', 'next')

# request 中 admin 字段名称
REQUEST_ADMIN_FIELD = getattr(settings, 'ADMIN_REQUEST_ADMIN_FIELD', 'admin')

# 登陆验证超时时间
AUTH_SLAT_TIMEOUT = getattr(settings, 'ADMIN_AUTH_SLAT_TIMEOUT', 120)

# 在线状态超时时间
ONLINE_TIMEOUT = getattr(settings, 'ADMIN_ONLINE_TIMEOUT', 10)

# 最大密码错误次数
LOGIN_MAX_FAILS = getattr(settings, 'ADMIN_LOGIN_MAX_FAILS', 3)

# 错误锁定时间
LOGIN_FAIL_LOCK_TIMES = getattr(settings, 'ADMIN_LOGIN_FAIL_LOCK_TIMES', 60 * 5)

# 使用客户端密码加密
CLIENT_PASSWORD_ENCRYPT = getattr(settings, 'ADMIN_CLIENT_PASSWORD_ENCRYPT', True)

# 管理后台标题名称,无HTML
TITLE_NAME = getattr(settings, 'ADMIN_TITLE_NAME', u'管理中心')

# 管理后台简称
SHORT_NAME = getattr(settings, 'ADMIN_SHORT_NAME', u'管理')

# 管理后台完整名称
FULL_NAME = getattr(settings, 'ADMIN_FULL_NAME', u'<b>管理</b>中心')

# 管理系统权限
ADMIN_PERMISSIONS = {
    'log.view': u'查看系统日志',
    'user.view': u'查看管理员',
}
