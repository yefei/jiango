# -*- coding: utf-8 -*-
# Created on 2015-9-1
# @author: Yefei
import hashlib
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils import timezone
from django.utils.functional import cached_property
from django.core.urlresolvers import reverse, NoReverseMatch
from jiango.serializers import serialize, deserialize
from jiango.shortcuts import update_instance
from .config import ONLINE_TIMEOUT, SECRET_KEY_DIGEST, LOGIN_FAIL_LOCK_TIMES, LOGIN_MAX_FAILS


def get_password_digest(raw_password):
    return hashlib.md5(hashlib.md5(raw_password).hexdigest() + SECRET_KEY_DIGEST).hexdigest()


class Permission(models.Model):
    codename = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(u'权限名', max_length=100)
    
    class Meta:
        ordering = ('codename',)
    
    def __unicode__(self):
        return ' | '.join(self.name.split('|'))


class Group(models.Model):
    name = models.CharField(u'名称', max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission, verbose_name=u'权限', blank=True)
    permissions.help_text = None  # 强制去除默认的 选择多个值 提示
    
    def __unicode__(self):
        return self.name


class UserManager(models.Manager):
    def online(self):
        online_gte = timezone.now() - timezone.timedelta(seconds=ONLINE_TIMEOUT)
        return self.exclude(login_token=None).filter(request_at__gte=online_gte)


class User(models.Model):
    username = models.CharField(u'用户名', max_length=30, unique=True)
    password_digest = models.CharField(max_length=32, editable=False)
    is_active = models.BooleanField(u'有效用户', default=True, db_index=True)
    is_superuser = models.BooleanField(u'超级用户', default=False, db_index=True)
    login_at = models.DateTimeField(null=True, db_index=True, editable=False)
    login_token = models.CharField(max_length=32, null=True, db_index=True, editable=False)
    login_fail_at = models.DateTimeField(u'最近登陆失败日期', null=True, db_index=True, editable=False)
    login_fails = models.PositiveSmallIntegerField(u'最近登陆失败次数', default=0, editable=False)
    join_at = models.DateTimeField(auto_now_add=True, db_index=True)
    request_at = models.DateTimeField(u'最近请求时间', null=True, db_index=True, editable=False)
    groups = models.ManyToManyField(Group, verbose_name=u'用户组', blank=True)
    groups.help_text = u'如果为超级用户则已经拥有所有用户组无需选择'
    permissions = models.ManyToManyField(Permission, verbose_name=u'额外权限', blank=True)
    permissions.help_text = u'如果为超级用户则已经拥有所有权限无需选择'
    objects = UserManager()
    
    class Meta:
        ordering = ('-request_at',)
        verbose_name = u'管理员'
    
    def __unicode__(self):
        return '%s #%d' % (self.username, self.pk)
    
    def update_password(self, password_digest):
        update_instance(self, password_digest=password_digest)
    
    @property
    def login_fail_lock_remain(self):
        if not self.login_fail_at:
            return 0
        return max(0, LOGIN_FAIL_LOCK_TIMES - (timezone.now() - self.login_fail_at).seconds)
    
    @property
    def is_login_fail_lock(self):
        return self.login_fail_lock_remain > 0 and self.login_fails >= LOGIN_MAX_FAILS
    
    def update_login_fails(self, fails=1):
        updates = {'login_fails': self.login_fails}
        if self.login_fail_at is None or self.login_fail_lock_remain == 0:
            updates['login_fail_at'] = timezone.now()
            updates['login_fails'] = 0
        updates['login_fails'] += fails
        update_instance(self, **updates)
    
    @cached_property
    def get_group_permissions(self):
        perms = Permission.objects.filter(group__user=self).values_list('codename')
        return set([i[0] for i in perms])
    
    @cached_property
    def get_all_permissions(self):
        perms = set([i[0] for i in self.permissions.values_list('codename')])
        perms.update(self.get_group_permissions)
        return perms
    
    @property
    def perm_stat(self):
        if not self.is_active:
            return u'无'
        if self.is_superuser:
            return u'全部'
        return len(self.get_all_permissions)
    
    def has_perm(self, codename):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return codename in self.get_all_permissions
    
    @property
    def is_login(self):
        return self.login_token is not None
    
    @property
    def online_remain(self):
        if not self.request_at:
            return 0
        return max(0, ONLINE_TIMEOUT - (timezone.now() - self.request_at).seconds)
    
    @property
    def is_online(self):
        return self.is_login and self.online_remain > 0
    
    def update_request_at(self, request_at=None):
        update_instance(self, request_at=(request_at or timezone.now()))


@receiver(pre_delete, sender=User)
def user_pre_delete(instance, **kwargs):
    # 不采用 ForeignKey(on_delete=models.SET_NULL) 避免查询 Log.user 增强性能
    Log.objects.filter(user=instance).update(user=None)


class LogTypes(object):
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    
    LEVELS = (
        (DEBUG, u'调试'),
        (INFO, u'信息'),
        (SUCCESS, u'成功'),
        (WARNING, u'注意'),
        (ERROR, u'错误'),
    )
    
    NONE = 0
    CREATE = 10
    RETRIEVE = 20
    UPDATE = 30
    DELETE = 40
    LOGIN = 1000
    LOGOUT = 1001
    
    ACTIONS = (
        (NONE, u'无'),
        (CREATE, u'增加'),
        (RETRIEVE, u'读取'),
        (UPDATE, u'更新'),
        (DELETE, u'删除'),
        (LOGIN, u'登陆'),
        (LOGOUT, u'退出'),
    )


class Log(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, verbose_name=u'用户')
    username = models.CharField(u'用户名', max_length=50, null=True)
    datetime = models.DateTimeField(u'时间', auto_now=True, db_index=True)
    level = models.SmallIntegerField(u'级别', db_index=True, choices=LogTypes.LEVELS, default=LogTypes.SUCCESS)
    action = models.SmallIntegerField(u'动作', db_index=True, choices=LogTypes.ACTIONS, default=LogTypes.NONE)
    app_label = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    view_name = models.CharField(max_length=100, null=True)
    view_args = models.CharField(max_length=100, null=True)
    view_kwargs = models.CharField(max_length=100, null=True)
    remote_ip = models.IPAddressField(null=True)
    
    class Meta:
        ordering = ('-id',)
    
    @classmethod
    def write(cls, level=LogTypes.SUCCESS, app_label=None, content=None, action=LogTypes.NONE,
              view_name=None, view_args=None, view_kwargs=None,
              remote_ip=None, user=None):
        _view_args = None
        _view_kwargs = None
        if view_args:
            _view_args = serialize('json', view_args)
        if view_kwargs:
            _view_kwargs = serialize('json', view_kwargs)
        return cls.objects.create(level=level, action=action, app_label=app_label,
                                  content=content, view_name=view_name,
                                  view_args=_view_args, view_kwargs=_view_kwargs,
                                  remote_ip=remote_ip, user=user, username=(unicode(user) if user else None))
    
    @cached_property
    def view_url(self):
        if self.view_name:
            args = deserialize('json', str(self.view_args)) if self.view_args else None
            kwargs = deserialize('json', str(self.view_kwargs)) if self.view_kwargs else None
            try:
                return reverse(self.view_name, args=args, kwargs=kwargs)
            except NoReverseMatch:
                pass
    
    def app_verbose_name(self):
        from .loader import get_app_verbose_name
        return get_app_verbose_name(self.app_label)
