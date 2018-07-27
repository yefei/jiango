# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/7/27 Feiye
Version: $Id:$
"""
from django.conf import settings


# 最终用户模型
USER_MODEL = getattr(settings, 'ACCOUNT_USER_MODEL', 'account.User')

# 登录过期时间
LOGIN_TOKEN_EXPIRED_SECONDS = getattr(settings, 'ACCOUNT_LOGIN_TOKEN_EXPIRED_SECONDS', 60 * 60 * 24 * 30  )

# 密码错误锁定时间
LOGIN_FAIL_LOCK_TIMES = getattr(settings, 'ACCOUNT_LOGIN_FAIL_LOCK_TIMES', 60 * 5)

# 最大密码错误次数
LOGIN_MAX_FAILS = getattr(settings, 'ACCOUNT_LOGIN_MAX_FAILS', 3)

# 登录 cookie 名称
LOGIN_COOKIE_NAME = getattr(settings, 'ACCOUNT_LOGIN_COOKIE_NAME', 'loginToken')

# 登录 cookie 名称
LOGIN_COOKIE_DOMAIN = getattr(settings, 'ACCOUNT_LOGIN_COOKIE_DOMAIN', settings.SESSION_COOKIE_DOMAIN)

# 登录 header 名称，默认 Login-Token:
LOGIN_HEADER_NAME = getattr(settings, 'ACCOUNT_LOGIN_HEADER_NAME', 'HTTP_X_LOGIN_TOKEN')

# 登录 api 参数名称
LOGIN_API_PARAM_NAME = getattr(settings, 'ACCOUNT_LOGIN_API_PARAM_NAME', 'loginToken')

# 登录 view 名称
LOGIN_VIEW_NAME = getattr(settings, 'ACCOUNT_LOGIN_VIEW_NAME', 'login')
