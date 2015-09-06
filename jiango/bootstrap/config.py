# -*- coding: utf-8 -*-
# Created on 2015-9-6
# @author: Yefei
from django.conf import settings


BOOTSTRAP_COLUMN_COUNT = getattr(settings, 'BOOTSTRAP_COLUMN_COUNT', 12)
