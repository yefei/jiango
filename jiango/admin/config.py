# -*- coding: utf-8 -*-
# Created on 2015-9-2
# @author: Yefei
import hashlib
from django.conf import settings


SECRET_KEY_DIGEST = hashlib.md5(settings.SECRET_KEY).hexdigest()

# 身份验证 cookie 名称
COOKIE_NAME = 'jiango_admin_auth'

# 登陆跳转字段名称
LOGIN_NEXT_FIELD = 'next'

# request 中 admin 字段名称
REQUEST_ADMIN_FIELD = 'admin'

# 登陆验证超时时间
AUTH_SLAT_TIMEOUT = 30

# 在线状态超时时间
ONLINE_TIMEOUT = 60 * 10

# 最大密码错误次数
LOGIN_MAX_FAILS = 3

# 错误锁定时间
LOGIN_FAIL_LOCK_TIMES = 60 * 5

# 管理系统权限
ADMIN_PERMISSIONS = {
    'log.view': u'查看系统日志',
    'user.view': u'查看管理员',
}
