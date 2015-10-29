# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
import re
from django.conf import settings
from django.utils.datastructures import SortedDict


COLUMN_PATH_RE = re.compile(u'^[_\-\w\u4e00-\uE814]+$')
COLUMN_PATH_HELP = u'可以输入 a-z、0-9、横线、下划线、汉字，目录名不可用纯数字，用 / 来分割目录'

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
#        #'content_view': 'path.to.views.content',
#        #'actions': {}, # 如同 CONTENT_ACTIONS 配置，区别是只针对这个模型
#    },
}

# 扩展模型
if hasattr(settings, "JIANGO_CMS_MODELS"):
    CONTENT_MODELS.update(settings.JIANGO_CMS_MODELS)

# 内容列表分页数
CONTENT_PER_PAGE = 100

# 单次操作最多条数
CONTENT_ACTION_MAX_RESULTS = 100

# 通用动作
CONTENT_ACTIONS = SortedDict()
CONTENT_ACTIONS['hide'] = {
    'name': u'隐藏/显示',
    'icon': 'icon-eye-close',
    # 'button_class': '',
    'form': 'jiango.cms.forms.HideAction',
}
CONTENT_ACTIONS['delete'] = {
    'name': u'删除',
    'icon': 'icon-trash icon-white',
    'button_class': 'btn-warning',
    'form': 'jiango.cms.forms.DeleteAction',
}

# 扩展通用动作
if hasattr(settings, "JIANGO_CMS_ACTIONS"):
    CONTENT_MODELS.update(settings.JIANGO_CMS_ACTIONS)
