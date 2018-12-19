# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
import re
from django.conf import settings
from django.utils.datastructures import SortedDict
from jiango.settings import get_setting


PATH_RE = re.compile(u'^[_\-\w\u4e00-\uE814]+$')
PATH_HELP = u'可以输入 a-z、0-9、横线、下划线、汉字，目录名不可用纯数字，用 / 来分割目录'

# 列表页分页默认值
LIST_PER_PAGE = 30

# 内容模型
CONTENT_MODELS = {
#    # 示例内容模型
#    # 添加 jiango.cms.article 到 INSTALLED_APPS 才可使用
#    'article': {
#        'name': u'文章',
#        'model': 'jiango.cms.article.models.Article',
#        'form': 'jiango.cms.article.forms.ArticleForm',
#        #'form_meta_fields': ('field',),
#        #'index_view': 'path.to.views.index',
#        #'list_view': 'path.to.views.list',
#        #'content_view': 'path.to.views.content'
#    },
}

# 扩展模型
if hasattr(settings, "JIANGO_CMS_MODELS"):
    CONTENT_MODELS.update(settings.JIANGO_CMS_MODELS)

# 内容列表分页数
CONTENT_PER_PAGE = 100

# 单次操作最多条数
CONTENT_ACTION_MAX_RESULTS = 100

# 内容批量管理动作
CONTENT_ACTIONS = SortedDict()
CONTENT_ACTIONS['flag'] = {
    'name': u'标记为',
    'icon': 'fa fa-flag',
    'button_class': 'btn-info',
    'form': 'jiango.cms.forms.FlagAction',
}
CONTENT_ACTIONS['hide'] = {
    'name': u'隐藏/显示',
    'icon': 'fa fa-low-vision',
    # 'button_class': '',
    'form': 'jiango.cms.forms.HideAction',
}
CONTENT_ACTIONS['delete'] = {
    'name': u'删除',
    'icon': 'fa fa-trash',
    'button_class': 'btn-warning',
    'form': 'jiango.cms.forms.DeleteAction',
}

# 集合批量动作
COLLECTION_ACTIONS = SortedDict()
COLLECTION_ACTIONS['delete'] = {
    'name': u'从集合中删除',
    'icon': 'fa fa-trash',
    'button_class': 'btn-warning',
    'form': 'jiango.cms.forms.CollectionDeleteAction',
}


# 扩展通用动作
if hasattr(settings, "JIANGO_CMS_ACTIONS"):
    CONTENT_MODELS.update(settings.JIANGO_CMS_ACTIONS)

# 标记
FLAGS = [
    (0, u'无'),
    (1, u'推荐'),
] + get_setting('CMS_FLAGS', [])
