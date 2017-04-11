# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2017/4/11
"""
import os
import errno
import hashlib
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.move import file_move_safe
from django.core.files import locks


class HashFileSystemStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = os.path.join(settings.MEDIA_ROOT, 'hash')
        if base_url is None:
            base_url = settings.MEDIA_URL + 'hash/'
        super(HashFileSystemStorage, self).__init__(location, base_url)

    def path(self, name):
        name = os.path.join(name[:2], name[2:4], name)
        return super(HashFileSystemStorage, self).path(name)

    def save(self, name, content):
        # 计算内容 HASH
        md5 = hashlib.md5()
        for chunk in content.chunks():
            md5.update(chunk)
        name = md5.hexdigest()

        # 保存文件
        full_path = self.path(name)
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        try:
            if hasattr(content, 'temporary_file_path'):
                file_move_safe(content.temporary_file_path(), full_path)
                content.close()
            else:
                fd = os.open(full_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0))
                try:
                    locks.lock(fd, locks.LOCK_EX)
                    for chunk in content.chunks():
                        os.write(fd, chunk)
                finally:
                    locks.unlock(fd)
                    os.close(fd)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)

        return name

    def delete(self, name):
        pass

    def url(self, name):
        name = '/'.join((name[:2], name[2:4], name))
        return super(HashFileSystemStorage, self).url(name)

hash_file_storage = HashFileSystemStorage()
