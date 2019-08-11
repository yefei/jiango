# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/12
"""
from jiango.settings import PrefixSetting


setting = PrefixSetting('CLOUD_UPLOAD_')


# 必须配置项
ACCESS_KEY = setting.get_setting('ACCESS_KEY')
SECRET_KEY = setting.get_setting('SECRET_KEY')
DOMAIN = setting.get_setting('DOMAIN')
BUCKET = setting.get_setting('BUCKET')

# 访问协议
PROTOCOL = setting.get_setting('PROTOCOL', 'http')

# 上传文件存储前缀
KEY_PREFIX = setting.get_setting('KEY_PREFIX', 'upload/')

# 临时文件前缀
TEMP_PREFIX = setting.get_setting('TEMP_PREFIX', 'temp/')

# 上传限制
SIZE_LIMIT = setting.get_setting('SIZE_LIMIT', 1024 * 1024 * 10)
MIME_LIMIT = setting.get_setting('MIME_LIMIT', '*/*')
