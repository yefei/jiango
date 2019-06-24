# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2018/7/27 Feiye
Version: $Id:$
"""
import hashlib
import uuid
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
from jiango.shortcuts import update_instance
from jiango.utils.http import get_remote_ip
from .signals import user_login_signal, user_logout_signal
from .settings import USER_MODEL, LOGIN_FAIL_LOCK_TIMES, LOGIN_MAX_FAILS, LOGIN_TOKEN_EXPIRED_SECONDS


_user_model = None


def get_user_model():
    global _user_model
    if _user_model is None:
        app_label, model_name = USER_MODEL.split('.')
        _user_model = models.get_model(app_label, model_name)
    return _user_model


class UserBase(models.Model):
    registered_at = models.DateTimeField(u'注册日期', default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(u'更新日期', auto_now=True, db_index=True)
    login_fail_at = models.DateTimeField(u'最近登陆失败日期', null=True, db_index=True, editable=False)
    login_fails = models.PositiveSmallIntegerField(u'最近登陆失败次数', default=0, editable=False)

    class Meta:
        abstract = True
        ordering = ['-pk']

    def __unicode__(self):
        return 'User#%s' % self.pk

    def get_request_client(self, request=None):
        u"""
        获取登录客户端，需要由继承类实现
        :param request: 当前请求
        :return: 返回客户端字符串描述
        """
        return None

    def login(self, request=None):
        u"""
        登录并返回一个有效的 LoginToken
        :param request: 当前请求
        :return: Login实例
        """
        token = hashlib.md5(uuid.uuid4().bytes).hexdigest()
        login = Login.objects.create(user=self,
                                     token=token,
                                     ip=get_remote_ip(request),
                                     client=self.get_request_client(request))
        user_login_signal.send(None, user=self, login=login, request=request)
        return login

    def logout(self, token=None, request=None):
        u"""
        退出登录
        :param token: 需要退出的loginToken,如果为空则退出所有loginToken
        :param request: 当前请求
        """
        if token:
            try:
                login = Login.objects.get(user=self, token=token)
            except Login.DoesNotExist:
                pass
            else:
                login.logout(request)
        else:
            Login.objects.filter(user=self, logout_at=None).update(logout_at=datetime.now())
            user_logout_signal.send(None, user=self, login=None, request=request)

    @property
    def login_fail_lock_remain(self):
        u"""
        登录失败锁定剩余时间
        :return: 剩余秒数
        """
        if not self.login_fail_at:
            return 0
        return max(0, LOGIN_FAIL_LOCK_TIMES - (datetime.now() - self.login_fail_at).seconds)

    @property
    def is_login_fail_lock(self):
        u"""
        是否登录失败锁定
        :return: True锁定, False正常
        """
        return self.login_fail_lock_remain > 0 and self.login_fails >= LOGIN_MAX_FAILS

    def update_login_fails(self, fails=1):
        u"""
        更新登录错误次数
        :param fails: 需要增加的次数
        """
        updates = {'login_fails': self.login_fails}
        if self.login_fail_at is None or self.login_fail_lock_remain == 0:
            updates['login_fail_at'] = datetime.now()
            updates['login_fails'] = 0
        updates['login_fails'] += fails
        update_instance(self, **updates)


class Login(models.Model):
    user = models.ForeignKey(USER_MODEL, editable=False)
    token = models.CharField(max_length=32, unique=True)
    ip = models.IPAddressField(u'登录IP', null=True, db_index=True)
    client = models.CharField(u'客户端', max_length=16, null=True, db_index=True)
    login_at = models.DateTimeField(u'登录日期', auto_now_add=True, db_index=True)
    request_at = models.DateTimeField(u'请求日期', auto_now=True, db_index=True)
    logout_at = models.DateTimeField(u'退出日期', null=True, db_index=True)

    class Meta:
        ordering = ['-login_at']

    def __unicode__(self):
        return u'id=%d, user=%r, at=%s' % (self.pk, self.user, self.login_at)

    @property
    def is_expired(self):
        return self.login_at + timedelta(seconds=LOGIN_TOKEN_EXPIRED_SECONDS) < datetime.now()

    @property
    def is_active(self):
        return self.logout_at is None and not self.is_expired

    def do_request(self, request=None):
        update_instance(self, request_at=datetime.now())

    def logout(self, request=None):
        update_instance(self, logout_at=datetime.now())
        user_logout_signal.send(None, user=self.user, login=self, request=request)
