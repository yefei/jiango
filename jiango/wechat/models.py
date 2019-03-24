# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/24
"""
from django.db import models
from django.utils import timezone


class Auth(models.Model):
    openid = models.CharField(u'OpenID', max_length=50, unique=True)
    access_token = models.CharField(u'调用凭证', max_length=200)
    access_expired_at = models.DateTimeField(u'调用有效期到')
    refresh_token = models.CharField(u'刷新凭证', max_length=200)
    refresh_expired_at = models.DateTimeField(u'刷新有效期到')
    scope = models.CharField(u'作用域', max_length=50)
    created_at = models.DateTimeField(u'创建日期', auto_now_add=True)
    updated_at = models.DateTimeField(u'更新日期', auto_now=True)

    class Meta:
        verbose_name = u'微信用户授权'
        ordering = ['-pk']

    def __unicode__(self):
        return u'%d:%s' % (self.pk, self.openid)

    @property
    def is_access_expired(self):
        return timezone.now() > self.access_expired_at

    @property
    def is_refresh_expired(self):
        return timezone.now() > self.refresh_expired_at
