# -*- coding: utf-8 -*-
# Created on 2015-10-8
# @author: Yefei
from django.db import models
from django.db.models.deletion import SET_NULL
from jiango.admin.models import User


class Column(models.Model):
    name = models.CharField(u'栏目名称', max_length=200)
    path = models.CharField(u'栏目路径', max_length=200, unique=True)
    sort = models.SmallIntegerField(u'排序', db_index=True, default=0)
    create_at = models.DateTimeField(u'创建日期', auto_now_add=True)
    update_at = models.DateTimeField(u'更新日期', auto_now=True)
    create_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False)
    views = models.PositiveIntegerField(u'浏览量', db_index=True, default=0, editable=False)
    
    class Meta:
        ordering = ('sort',)


class Content(models.Model):
    column = models.ForeignKey(Column)
