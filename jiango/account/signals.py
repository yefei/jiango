# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/5/11
Version: $Id: signals.py 728 2018-05-11 07:52:43Z feiye $
"""
from django.dispatch import Signal


user_login_signal = Signal(providing_args=['user', 'login', 'request'])
user_logout_signal = Signal(providing_args=['user', 'login', 'request'])
