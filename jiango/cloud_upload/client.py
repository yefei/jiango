# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/12
"""
import qiniu
import requests
from qiniu.utils import etag_stream
from .settings import ACCESS_KEY, SECRET_KEY, PROTOCOL, DOMAIN, BUCKET, SIZE_LIMIT, MIME_LIMIT, TEMP_PREFIX


class StorageError(Exception):
    def __init__(self, action, ret, info):
        self.action = action
        self.ret = ret
        self.info = info

    def __str__(self):
        return '%s: %d' % (self.action, self.info.status_code)


storage_client = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
storage_bucket = qiniu.BucketManager(storage_client)


# 取得公开访问链接
def get_public_url(key, query_string=None):
    return '%s://%s/%s%s' % (PROTOCOL, DOMAIN, key, ('?' + query_string) if query_string else '')


# 取得私有访问链接
def get_private_url(key, query_string=None):
    return storage_client.private_download_url(get_public_url(key, query_string), expires=60 * 60 * 24)


# 获取上传 Token
def get_upload_token(**policy):
    return storage_client.upload_token(BUCKET, expires=60 * 60 * 24, policy=policy)


# 客户端上传凭证
def get_client_upload_token(size_limit=SIZE_LIMIT, mine_limit=MIME_LIMIT):
    _policy = dict(
        saveKey='%s$(etag)' % TEMP_PREFIX,
        mimeLimit=mine_limit,
        fsizeLimit=size_limit,
        returnBody='{"key":$(key)}',
    )
    return get_upload_token(**_policy)


def get_stream_hash(stream):
    return etag_stream(stream)


# 获取远程文件信息
def get_stat(key):
    ret, info = storage_bucket.stat(BUCKET, key)
    if info.status_code != 200:
        raise StorageError('get_stat', ret, info)
    return ret


# 移动文件到目标位置，相当于重命名
def move_file(src_key, dest_key):
    ret, info = storage_bucket.move(BUCKET, src_key, BUCKET, dest_key)
    if info.status_code == 200:
        # set_delete_after_days(dest_key, 0)
        return ret
    if info.status_code == 614:  # 目标资源已存在
        # delete_file(src_key)
        return True
    raise StorageError('move_file', ret, info)


# 复制文件到目标位置
def copy_file(src_key, dest_key):
    ret, info = storage_bucket.copy(BUCKET, src_key, BUCKET, dest_key)
    if info.status_code == 200:
        return ret
    if info.status_code == 614:  # 目标资源已存在
        return True
    raise StorageError('copy_file', ret, info)


# 设置远程文件自动删除天数
def set_delete_after_days(key, days=0):
    ret, info = storage_bucket.delete_after_days(BUCKET, key, str(days))
    if info.status_code != 200:
        raise StorageError('set_delete_after_days', ret, info)
    return ret


# 上传数据到云存储中
def put_data(key, data, mime_type=None):
    if mime_type is None:
        mime_type = 'application/octet-stream'
    token = get_upload_token()
    ret, info = qiniu.put_data(token, key, data, mime_type=mime_type)
    if info.status_code == 614:  # 目标资源已存在
        return True
    if info.status_code != 200:
        raise StorageError('put_data', ret, info)
    return ret


# 上传数据流到云存储中
def put_stream(key, stream, size, mime_type=None):
    if mime_type is None:
        mime_type = 'application/octet-stream'
    token = get_upload_token()
    ret, info = qiniu.put_stream(token, key, stream, file_name=key, data_size=size, mime_type=mime_type)
    if info.status_code == 614:  # 目标资源已存在
        return True
    if info.status_code != 200:
        raise StorageError('put_stream', ret, info)
    return ret


# 删除云文件
def delete_file(name):
    ret, info = storage_bucket.delete(BUCKET, name)
    if info.status_code != 200:
        raise StorageError('delete_file', ret, info)
    return ret


# 获取图片基础信息
# size          是   文件大小，单位：Bytes
# format	    是   图片类型，如png、jpeg、gif、bmp等。
# width         是   图片宽度，单位：像素(px)。
# height	    是   图片高度，单位：像素(px)。
# colorModel	是   彩色空间，如palette16、ycbcr等。
# frameNumber        帧数，gif 图片会返回此项。
def image_info(key):
    url = get_private_url(key, 'imageInfo')
    res = requests.get(url)
    if res.status_code != 200:
        raise StorageError('image_info', None, res)
    return res.json()


# 音视频信息
def av_info(key):
    url = get_private_url(key, 'avinfo')
    res = requests.get(url)
    if res.status_code != 200:
        raise StorageError('av_info', None, res)
    return res.json()
