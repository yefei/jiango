# -*- coding: utf-8 -*-
# Created on 2015-10-8
# @author: Yefei
from django.db import models
from django.db.models.deletion import SET_NULL
from django.dispatch import receiver
from django.db.models import signals
from jiango.admin.models import User
from .config import COLUMN_PATH_HELP


class ColumnManager(models.Manager):
    # 取得指定路径下的栏目, depth 可以选择获取深度， 0为一层 1为二层以此类推
    # Column.objects.children('news')
    def children(self, path='', depth=0):
        path = path.strip(' /')
        path_depth = path.count('/')
        qs = self
        if path != '':
            qs = qs.filter(path__istartswith=path + '/')
            path_depth += 1
        if depth == 0:
            qs = qs.filter(depth=path_depth)
        else:
            qs = qs.filter(depth__gte=path_depth,
                           depth__lte=path_depth + depth)
        return qs


class Column(models.Model):
    name = models.CharField(u'栏目名称', max_length=200)
    path = models.CharField(u'栏目路径', max_length=200, unique=True, help_text=COLUMN_PATH_HELP)
    depth = models.SmallIntegerField(u'栏目深度', db_index=True, editable=False)
    sort = models.SmallIntegerField(u'排序', db_index=True, default=0, editable=False)
    create_at = models.DateTimeField(u'创建日期', auto_now_add=True)
    update_at = models.DateTimeField(u'更新日期', auto_now=True)
    create_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    update_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    views = models.PositiveIntegerField(u'浏览量', db_index=True, default=0, editable=False)
    objects = ColumnManager()
    
    class Meta:
        ordering = ('sort',)
    
    def __unicode__(self):
        return self.path
    
    @property
    def parent_path(self):
        if self.depth > 0:
            return '/'.join(self.path.split('/')[:-1])
        return ''


@receiver(signals.pre_save, sender=Column)
def on_column_pre_save(instance, **kwargs):
    instance.path = instance.path.strip(' /')
    instance.depth = instance.path.count('/')
    if not instance.pk:
        try:
            parent_last = Column.objects.children(instance.parent_path).latest('sort')
            instance.sort = parent_last.sort + 1
        except Column.DoesNotExist:
            pass


class Content(models.Model):
    column = models.ForeignKey(Column)
