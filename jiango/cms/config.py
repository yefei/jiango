# -*- coding: utf-8 -*-
# Created on 2015-10-10
# @author: Yefei
import re
from django.conf import settings


COLUMN_PATH_RE = re.compile(u'^[_\-\w\u4e00-\uE814]+$')
COLUMN_PATH_HELP = u'可以输入 a-z、0-9、横线、下划线、汉字，目录名不可用纯数字，用 / 来分割目录'

# 列表页分页默认值
LIST_PER_PAGE = 30

# 内容模型
CONTENT_MODELS = {
    'article': {
        'name': u'文章',
        'model': 'jiango.cms.models.Article',
        'form': 'jiango.cms.forms.ArticleForm',
        #'form_meta_fields': ('is_hidden'),
        #'index_view': 'path.to.views.index',
        #'list_view': 'path.to.views.list',
        #'content_view': 'path.to.views.content',
    },
}

# 扩展模型
if hasattr(settings, "JIANGO_CMS_MODELS"):
    CONTENT_MODELS.update(settings.JIANGO_CMS_MODELS)
