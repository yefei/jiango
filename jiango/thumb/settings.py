# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2018/12/19
from jiango.settings import get_setting


# 缩略图访问前缀
THUMB_PREFIX = get_setting('THUMB_PREFIX', 'thumb')

# 缩略图存储路径
THUMB_ROOT = get_setting('THUMB_ROOT', '')

# 缩略图访问链接
THUMB_URL = get_setting('THUMB_URL', '/%s/' % THUMB_PREFIX)

# JPEG 品质
THUMB_JPEG_QUALITY = get_setting('THUMB_JPEG_QUALITY', 85)
