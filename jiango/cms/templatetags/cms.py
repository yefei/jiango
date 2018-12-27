# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/4/11
"""
from django.template import Library
from jiango.cms.shortcuts import cms_contents, cms_collections


register = Library()

register.assignment_tag(cms_contents)
register.assignment_tag(cms_collections)
