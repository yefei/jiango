# -*- coding: utf-8 -*-
# Created on 2015-9-5
# @author: Yefei
from django import template
from jiango.pagination import paginate


register = template.Library()
register.inclusion_tag('admin/paginate.tag.html')(paginate)
