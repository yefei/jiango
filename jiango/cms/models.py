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
from django.core.cache import cache
from jiango.shortcuts import update_instance
from jiango.admin.models import User
from jiango.importlib import import_object
from .config import PATH_HELP, CONTENT_MODELS, LIST_PER_PAGE, FLAGS


INDEX_TEMPLATE_HELP = u'默认模版: cms/index'
LIST_TEMPLATE_HELP = u'默认模版: cms/list'
CONTENT_TEMPLATE_HELP = u'默认模版: cms/content'

PATH_TREE_CACHE_KEY = 'cms:path:tree'

PATH_DEPTH_FIRST = 1
PATH_DEPTH_ALL = -1


class PathQuerySet(QuerySet):
    # 取得指定路径下的栏目, depth 可以选择获取深度，1为一层 2为二层...
    # Path.objects.children('news')
    def children(self, path=u'', depth=PATH_DEPTH_FIRST):
        path = path.strip(' /')
        qs = self
        if path != '':
            qs = qs.filter(path__istartswith=path + '/')
        if depth != PATH_DEPTH_ALL:
            path_depth = path.count('/') + 1
            if depth == PATH_DEPTH_FIRST:
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
                if p not in ref:
                    ref[p] = [None, SortedDict()]
                col = ref[p]
                ref = ref[p][1]
            col[0] = i
        return out


class PathManager(models.Manager):
    def get_query_set(self):
        return PathQuerySet(self.model, using=self._db)
    
    def children(self, path=u'', depth=0):
        return self.get_query_set().children(path, depth)
    
    def tree(self, path=''):
        return self.get_query_set().tree(path)

    def cached_tree(self):
        tree = cache.get(PATH_TREE_CACHE_KEY)
        if tree is None:
            tree = self.tree()
            cache.set(PATH_TREE_CACHE_KEY, tree)
        return tree


class ModelBase(models.Model):
    model = models.CharField(u'内容模型', max_length=50, choices=((k, i['name']) for k, i in CONTENT_MODELS.items()))

    class Meta:
        abstract = True

    @property
    def model_config(self):
        return CONTENT_MODELS.get(self.model)

    @property
    def model_class(self):
        return import_object(self.model_config.get('model'))

    @property
    def form_class(self):
        return import_object(self.model_config.get('form'))


class Path(ModelBase):
    VIEW_INDEX = 1
    VIEW_LIST = 2
    VIEW_CONTENT = 3
    VIEW_CHOICES = (
        (VIEW_INDEX, u'首页'),
        (VIEW_LIST, u'列表'),
        (VIEW_CONTENT, u'内容'),
    )

    name = models.CharField(u'栏目名称', max_length=100)
    path = models.CharField(u'栏目路径', max_length=200, unique=True, help_text=PATH_HELP)
    depth = models.SmallIntegerField(u'栏目深度', db_index=True, editable=False)
    sort = models.SmallIntegerField(u'排序', db_index=True, default=0, editable=False)
    
    index_template = models.CharField(u'首页模版', max_length=100, blank=True, default='', help_text=INDEX_TEMPLATE_HELP)
    list_template = models.CharField(u'列表模版', max_length=100, blank=True, default='', help_text=LIST_TEMPLATE_HELP)
    list_per_page = models.PositiveSmallIntegerField(u'列表页数据分页条数', default=LIST_PER_PAGE)
    content_template = models.CharField(u'内容模版', max_length=200, blank=True, default='', help_text=CONTENT_TEMPLATE_HELP)
    default_view = models.SmallIntegerField(u'默认视图', choices=VIEW_CHOICES, default=VIEW_LIST, db_index=True)
    
    create_at = models.DateTimeField(u'创建日期', auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(u'更新日期', auto_now=True, db_index=True)
    create_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    update_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    views = models.PositiveIntegerField(u'浏览量', db_index=True, default=0, editable=False)

    objects = PathManager()
    
    class Meta:
        ordering = ('id',)
        get_latest_by = ('id',)
    
    def __unicode__(self):
        return self.path
    
    @models.permalink
    def get_absolute_url(self):
        return 'cms-path', [self.path]

    url = property(get_absolute_url)
    
    @property
    def parent_path(self):
        if self.depth > 0:
            return '/'.join(self.path.split('/')[:-1])
        return ''
    
    def children(self, depth=PATH_DEPTH_FIRST):
        return Path.objects.children(self.path, depth)

    @cached_property
    def content_count(self):
        return ContentBase.objects.filter(path=self, is_deleted=False).count()
    
    # 同步更新内容中的 path 和 depth
    def update_content_path(self):
        ContentBase.objects.filter(path=self).update(path_value=self.path, path_depth=self.depth)


@receiver(signals.pre_save, sender=Path)
def on_path_pre_save(instance, **kwargs):
    instance.path = instance.path.strip(' /')
    instance.depth = instance.path.count('/')
    if not instance.pk:
        try:
            parent_last = Path.objects.children(instance.parent_path).latest()
            instance.sort = parent_last.sort + 1
        except Path.DoesNotExist:
            pass
    # 修改子栏目的父路径
    if instance.pk:
        p = Path.objects.get(pk=instance.pk)
        if p.path != instance.path:
            for i in p.children(PATH_DEPTH_ALL):
                path = instance.path + i.path[len(p.path):]
                update_instance(i, path=path)
                i.update_content_path()


@receiver(signals.post_save, sender=Path)
def on_path_post_save(instance, **kwargs):
    instance.update_content_path()
    cache.delete(PATH_TREE_CACHE_KEY)


class Collection(models.Model):
    name = models.CharField(u'集合名称', max_length=100, unique=True)

    class Meta:
        ordering = ['pk']
        verbose_name = u'内容集合'

    def __unicode__(self):
        return self.name

    @cached_property
    def content_count(self):
        return self.contentbase_set.filter(is_deleted=False).count()


class CollectionContent(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    contentbase = models.ForeignKey('ContentBase', on_delete=models.CASCADE)

    class Meta:
        auto_created = False
        ordering = ['-pk']
        db_table = 'cms_contentbase_collections'
        verbose_name = u'内容集合关联'

    def __unicode__(self):
        return self.contentbase.title


class ContentQuerySet(QuerySet):
    # 返回可用的内容
    def available(self):
        return self.filter(is_deleted=False, is_hidden=False)


class ContentManager(models.Manager):
    def get_query_set(self):
        return ContentQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_query_set().available()


class ContentBase(ModelBase):
    path = models.ForeignKey(Path, editable=False, related_name='+')
    path_value = models.CharField(max_length=200, db_index=True, editable=False)  # 缓存字段:用于快速检索
    path_depth = models.SmallIntegerField(db_index=True, editable=False)  # 缓存字段:用于快速检索
    title = models.CharField(u'标题', max_length=200, null=True)
    create_at = models.DateTimeField(u'创建日期', auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(u'更新日期', auto_now=True, db_index=True)
    create_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    update_user = models.ForeignKey(User, null=True, on_delete=SET_NULL, editable=False, related_name='+')
    views = models.PositiveIntegerField(u'浏览量', db_index=True, default=0, editable=False)
    flag = models.SmallIntegerField(u'标记为', default=0, db_index=True, choices=FLAGS)
    is_deleted = models.BooleanField(u'已删除?', db_index=True, default=False, editable=False)
    is_hidden = models.BooleanField(u'隐藏 (在前台不显示)', db_index=True, default=False)
    collections = models.ManyToManyField(Collection, blank=True, verbose_name=u'内容集合',
                                         help_text=u'可以将此内容归集到多个集合中。')
    objects = ContentManager()

    class Meta:
        ordering = ('-pk',)
        get_latest_by = ('pk', )

    def __unicode__(self):
        return self.title or ('Content: #%d' % self.pk)

    @models.permalink
    def get_absolute_url(self):
        return 'cms-content', [self.path_value, self.pk]

    url = property(get_absolute_url)
    
    def is_available(self):
        return not self.is_deleted and not self.is_hidden

    @property
    def model_name(self):
        return self.model_config.get('name')

    @cached_property
    def previous(self):
        try:
            return self.model_class.objects.filter(
                is_deleted=False, is_hidden=False, path=self.path, pk__lt=self.pk).order_by('pk')[0]
        except IndexError:
            pass

    @cached_property
    def next(self):
        try:
            return self.model_class.objects.filter(
                is_deleted=False, is_hidden=False, path=self.path, pk__gt=self.pk).order_by('-pk')[0]
        except IndexError:
            pass


########################################################################################################################

MENUS_CACHE_KEY = 'jiango.menus'


class Menu(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, verbose_name=u'父')

    title = models.CharField(u'标题', max_length=200)
    value = models.TextField(u'值')
    order = models.IntegerField(u'排序值', db_index=True, blank=True, help_text=u'不填写默认为最后一项')
    is_hidden = models.BooleanField(u'隐藏', default=False)

    created_at = models.DateTimeField(u'创建日期', auto_now_add=True)
    updated_at = models.DateTimeField(u'更新日期', auto_now=True, db_index=True)

    class Meta:
        ordering = ['order']
        get_latest_by = 'order'

    def __unicode__(self):
        return self.title

    @property
    def is_menu(self):
        return self.parent_id is None

    @property
    def is_item(self):
        return not self.is_menu

    @property
    def parents(self):
        if self.is_menu:
            return [self]
        return self.parent.parents + [self]

    @property
    def level(self):
        return len(self.parents) - 1

    def get_children(self):
        if not hasattr(self, '_children'):
            self._children = self.menu_set.all()
        return self._children

    def set_children(self, v):
        self._children = v

    children = property(get_children, set_children)


def get_all_menus():
    """
    取得所有菜单项，排序并设置 parent 和 children 防止数据重复读取
    :return:
    """
    item_set = set(Menu.objects.all())

    def child(item):
        for c in item_set:
            if item.parent_id == c.pk:
                item.parent = c
                item.children = list(child(x) for x in item_set if x.parent_id == item.pk)
                break
        return item

    for i in item_set:
        # 顶层菜单
        if i.parent_id is None:
            i.children = list(child(x) for x in item_set if x.parent_id == i.pk)
            yield i


def flat_all_menus(items, exclude=None):
    """
    平面化菜单项，按照父子关系优先顺序
    :param items: 需要平面化的项目
    :param exclude: 需要排除的项目，同时排除子项
    :return:
    """
    for i in items:
        if i == exclude:
            continue
        yield i
        for x in flat_all_menus(i.children, exclude):
            yield x


def get_cache_menus():
    items = cache.get(MENUS_CACHE_KEY)
    if not items:
        items = set(get_all_menus())
        cache.set(MENUS_CACHE_KEY, items)
    return items


@receiver(signals.pre_save, sender=Menu)
def on_menu_pre_save(instance, **kwargs):
    if instance.order is None or instance.parent_id != Menu.objects.get(pk=instance.pk).parent_id:
        try:
            last_obj = Menu.objects.filter(parent=instance.parent).latest()
        except Menu.DoesNotExist:
            last_obj = None
        instance.order = last_obj.order + 1 if last_obj else 0


@receiver(signals.post_save, sender=Menu)
@receiver(signals.post_delete, sender=Menu)
def on_menu_update(**kwargs):
    cache.delete(MENUS_CACHE_KEY)
