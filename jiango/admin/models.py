# -*- coding: utf-8 -*-
# Created on 2015-9-1
# @author: Yefei
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from jiango.serializers import serialize


ONLINE_TIMEOUT = 30


class AbstractPermission(models.Model):
    app_label = models.CharField(max_length=100)
    codename = models.CharField(max_length=100)
    
    class Meta:
        abstract = True


class Group(models.Model):
    name = models.CharField(u'名称', max_length=80, unique=True)


class GroupPermission(AbstractPermission):
    group = models.ForeignKey(Group, related_name='permission_set')
    
    class Meta:
        unique_together = (('group', 'app_label', 'codename'),)


class UserManager(models.Manager):
    def online(self):
        online_gte = timezone.now() - timezone.timedelta(seconds=ONLINE_TIMEOUT)
        return self.filter(is_login=True, request_at__gte=online_gte)


class User(models.Model):
    username = models.CharField(u'用户名', max_length=30, unique=True)
    password_digest = models.CharField(max_length=32, editable=False)
    is_active = models.BooleanField(u'有效用户', default=True, db_index=True)
    is_superuser = models.BooleanField(u'超级用户', default=False, db_index=True)
    is_login = models.BooleanField(u'已经登陆', default=False, db_index=True)
    login_at = models.DateTimeField(null=True, db_index=True, editable=False)
    login_fails = models.PositiveSmallIntegerField(u'尝试登陆失败次数', default=0, editable=False)
    join_at = models.DateTimeField(auto_now_add=True, db_index=True)
    request_at = models.DateTimeField(u'请求时间', null=True, db_index=True, editable=False)
    groups = models.ManyToManyField(Group, verbose_name=u'用户组', blank=True)
    objects = UserManager()
    
    class Meta:
        ordering = ('-request_at',)
    
    def __unicode__(self):
        return '%d: %s' % (self.pk, self.username)
    
    @cached_property
    def get_group_permissions(self):
        user_groups_field = self._meta.get_field('groups')
        user_groups_query = 'group__%s' % user_groups_field.related_query_name()
        perms = GroupPermission.objects.filter(**{user_groups_query: self})
        perms = perms.values_list('app_label', 'codename').order_by()
        return set(['%s.%s' % (app_label, codename) for app_label, codename in perms])
    
    @cached_property
    def get_all_permissions(self):
        perms = set(['%s.%s' % (i.app_label, i.codename) for i in self.permission_set.all()])
        perms.update(self.get_group_permissions)
        return perms
    
    @property
    def perm_stat(self):
        if not self.is_active:
            return u'无'
        if self.is_superuser:
            return u'全部'
        return len(self.get_all_permissions)
    
    def has_perm(self, perm_name):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return perm_name in self.get_all_permissions
    
    @property
    def is_online(self):
        return self.is_login and self.request_at and self.request_at >= (timezone.now() - timezone.timedelta(seconds=ONLINE_TIMEOUT))


class UserPermission(AbstractPermission):
    user = models.ForeignKey(User, related_name='permission_set')
    
    class Meta:
        unique_together = (('user', 'app_label', 'codename'),)


class Log(models.Model):
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
    ACTIONS = (
        (NONE, u'无'),
        (CREATE, u'增加'),
        (RETRIEVE, u'读取'),
        (UPDATE, u'更新'),
        (DELETE, u'删除'),
    )
    
    user = models.ForeignKey(User, null=True, verbose_name=u'用户')
    datetime = models.DateTimeField(u'时间', auto_now=True, db_index=True)
    level = models.SmallIntegerField(u'级别', db_index=True, choices=LEVELS, default=SUCCESS)
    action = models.SmallIntegerField(u'动作', db_index=True, choices=ACTIONS, default=NONE)
    app_label = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    view_name = models.CharField(max_length=100, null=True)
    view_args = models.CharField(max_length=100, null=True)
    view_kwargs = models.CharField(max_length=100, null=True)
    remote_ip = models.IPAddressField(null=True)
    
    class Meta:
        ordering = ('-id',)
    
    @staticmethod
    def write(level=SUCCESS, action=NONE, app_label=None, content=None,
              view_name=None, view_args=None, view_kwargs=None,
              remote_ip=None, user=None):
        _view_args = None
        _view_kwargs = None
        if view_args:
            _view_args = serialize('json', view_args)
        if view_kwargs:
            _view_kwargs = serialize('json', view_kwargs)
        return Log.objects.create(level=level, action=action, app_label=app_label,
                   content=content,view_name=view_name,
                   view_args=_view_args, view_kwargs=_view_kwargs,
                   remote_ip=remote_ip, user=user)
    
    @property
    def view_url(self):
        if self.view_name:
            if not hasattr(self, '_view_url'):
                self._view_url = None
            return self._view_url
