# -*- coding: utf-8 -*-
# Created on 2015-10-8
# @author: Yefei
from django.db import models
from django.db.models.deletion import SET_NULL
from django.dispatch import receiver
from django.db.models import signals
from django.db.models.query import QuerySet
from django.utils.datastructures import SortedDict
from django.utils.functional import cached_property
from jiango.shortcuts import update_instance
from jiango.admin.models import User
from .utils import get_model_object, get_model_actions
from .config import COLUMN_PATH_HELP, CONTENT_MODELS, LIST_PER_PAGE


INDEX_TEMPLATE_HELP = u'默认模版: cms/index'
LIST_TEMPLATE_HELP = u'默认模版: cms/list'
CONTENT_TEMPLATE_HELP = u'默认模版: cms/content'


class ColumnQuerySet(QuerySet):
    # 取得指定路径下的栏目, depth 可以选择获取深度，-1所有层 0为一层 1为二层以此类推
    # Column.objects.children('news')
    def children(self, path='', depth=0):
        path = path.strip(' /')
        path_depth = path.count('/')
        qs = self
        if path != '':
            qs = qs.filter(path__istartswith=path + '/')
            path_depth += 1
        if depth > -1:
            if depth == 0:
                qs = qs.filter(depth=path_depth)
            else:
                qs = qs.filter(depth__gte=path_depth,
                               depth__lte=path_depth + depth)
        return qs
    
    # 返回树形字典
    def tree(self, path=''):
        qs = self.filter(path__istartswith=path + '/') if path else self.all()
        out = SortedDict()
        for i in qs:
            ref = out
            col = []
            paths = i.path.split('/')
            for p in paths:
                if not ref.has_key(p):
                    ref[p] = [None, SortedDict()]
                col = ref[p]
                ref = ref[p][1]
            col[0] = i
        return out


class ColumnManager(models.Manager):
    def get_query_set(self):
        return ColumnQuerySet(self.model, using=self._db)
    
    def children(self, path='', depth=0):
        return self.get_query_set().children(path, depth)
    
    def tree(self, path=''):
        return self.get_query_set().tree(path)


class Column(models.Model):
    model = models.CharField(u'内容模型', max_length=50, blank=True, default='',
                             choices=((k, i['name']) for k, i in CONTENT_MODELS.items()),
                             help_text=u'如不选则为不可发布类型，选定模型后不可再次修改')
    name = models.CharField(u'栏目名称', max_length=100)
    path = models.CharField(u'栏目路径', max_length=200, unique=True, help_text=COLUMN_PATH_HELP)
    depth = models.SmallIntegerField(u'栏目深度', db_index=True, editable=False)
    sort = models.SmallIntegerField(u'排序', db_index=True, default=0, editable=False)
    
    index_template = models.CharField(u'首页模版', max_length=100, blank=True, default='', help_text=INDEX_TEMPLATE_HELP)
    list_template = models.CharField(u'列表模版', max_length=100, blank=True, default='', help_text=LIST_TEMPLATE_HELP)
    list_per_page = models.PositiveSmallIntegerField(u'列表页数据分页条数', default=LIST_PER_PAGE)
    content_template = models.CharField(u'内容模版', max_length=200, blank=True, default='', help_text=CONTENT_TEMPLATE_HELP)
    
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
    
    @models.permalink
    def get_absolute_url(self):
        return 'cms-column', [self.path]
    
    @property
    def parent_path(self):
        if self.depth > 0:
            return '/'.join(self.path.split('/')[:-1])
        return ''
    
    def children(self, depth=0):
        return Column.objects.children(self.path, depth)
    
    def get_model_object(self, key):
        if self.model:
            return get_model_object(self.model, key)
    
    def get_content_actions(self):
        if self.model:
            return get_model_actions(self.model)
    
    @cached_property
    def content_count(self):
        Model = self.get_model_object('model')
        if Model:
            return Model.objects.filter(column=self).count()
        return 0
    
    # 同步更新内容中的 path 和 depth
    def update_content_path(self):
        Model = self.get_model_object('model')
        if Model:
            Model.objects.filter(column=self).update(column_path=self.path,
                                                     column_depth=self.depth)


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
    # 修改子栏目的父路径
    if instance.pk:
        col = Column.objects.get(pk=instance.pk)
        if col.path != instance.path:
            for i in col.children(-1):
                path = instance.path + i.path[len(col.path):]
                update_instance(i, path=path)
                i.update_content_path()


@receiver(signals.post_save, sender=Column)
def on_column_post_save(instance, **kwargs):
    instance.update_content_path()


class ContentQuerySet(QuerySet):
    # 返回可用的内容
    def available(self):
        return self.filter(is_deleted=False, is_hidden=False)


class ContentManager(models.Manager):
    def get_query_set(self):
        return ContentQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_query_set().available()


class ContentBase(models.Model):
    column = models.ForeignKey(Column, editable=False, related_name='+')
    column_path = models.CharField(u'栏目路径', max_length=200, db_index=True, editable=False)
    column_depth = models.SmallIntegerField(u'栏目深度', db_index=True, editable=False)
    create_at = models.DateTimeField(u'创建日期', auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(u'更新日期', auto_now=True, db_index=True)
    create_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    update_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    views = models.PositiveIntegerField(u'浏览量', db_index=True, default=0, editable=False)
    is_deleted = models.BooleanField(u'已删除?', db_index=True, default=False, editable=False)
    is_hidden = models.BooleanField(u'隐藏 (在前台不显示)', db_index=True, default=False)
    objects = ContentManager()
    
    class Meta:
        abstract = True
        ordering = ('-pk',)
    
    @models.permalink
    def get_absolute_url(self):
        return 'cms-content', [self.column_path, self.pk]
    
    def is_available(self):
        return not self.is_deleted and not self.is_hidden
