# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/5/24 Feiye
Version: $Id:$
"""
from django.conf import settings
from jiango.api import api
from jiango.api.exceptions import Deny, ParamError
from jiango.api.helpers import api_result
from .models import User
from .auth import set_login, set_login_cookie
from .views import log


@api
def dev_login(request, response):
    if not settings.DEBUG:
        raise Deny()
    username = request.param('username')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise ParamError('username does not exits')
    set_login(user)
    set_login_cookie(response, user)
    log(request, log.SUCCESS, u'用户 %s 登陆成功' % user.username, log.LOGIN, user=user)
    return api_result()
