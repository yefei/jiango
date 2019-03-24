# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/3/22
Version: $Id: errorcodes.py 705 2018-04-24 09:17:08Z feiye $
"""

SUCCESS = 0         # 成功，没有任何错误
ERROR = -1          # 常规错误类型
FROM_ERROR = -2     # 表单错误
UNKNOWN_ERROR = -100  # 未知错误类型

LOGIN_AUTH_FAIL = 1000, u'登录验证失败'

CAPTCHA_ERROR = 1001, u'图像验证码错误'

WECHAT_AUTH_REQUIRED = 1002, u'需要微信登陆授权'
