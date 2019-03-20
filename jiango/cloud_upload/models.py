# -*- coding: utf-8 -*-
# created by YeFei<316606233@qq.com>
# since 2019/1/19
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from .client import delete_file, get_public_url


class File(models.Model):
    size = models.PositiveIntegerField(u'大小')
    hash = models.CharField(u'HASH', max_length=32, unique=True)
    mime = models.CharField(u'文件类型', max_length=60, db_index=True, null=True)
    width = models.PositiveSmallIntegerField(u'宽度', default=0)
    height = models.PositiveSmallIntegerField(u'高度', default=0)
    created_at = models.DateTimeField(u'创建日期', auto_now_add=True)

    class Meta:
        ordering = ['-pk']
        verbose_name = u'云文件'

    def __unicode__(self):
        return self.hash

    @property
    def is_image(self):
        return self.mime and self.mime.startswith('image/')

    @property
    def is_video(self):
        return self.mime and self.mime.startswith('video/')

    @property
    def key(self):
        from .settings import KEY_PREFIX
        return KEY_PREFIX + self.hash

    @property
    def url(self):
        return get_public_url(self.key)


@receiver(signals.post_delete, sender=File)
def on_file_post_delete(instance, **kwargs):
    # 删除实体文件
    delete_file(instance.key)


class CloudFileField(models.ForeignKey):
    def __init__(self, **kwargs):
        super(CloudFileField, self).__init__(File, **kwargs)

    def save_form_data(self, instance, data):
        # 如果不是 File 类型，可能是 File id 或者 hash
        # CloudClearableFileInput, 不修改状态下传回 file ID
        if data and not isinstance(data, File):
            if isinstance(data, basestring):
                data = File.objects.get(hash=data)
            else:
                data = File.objects.get(pk=data)
        # CloudClearableFileInput 清除
        if not data:
            data = None
        setattr(instance, self.name, data)

    def formfield(self, **kwargs):
        form_class = kwargs.pop('form_class', None)
        if form_class is None:
            from .forms import CloudFileFormField
            form_class = CloudFileFormField
        return super(CloudFileField, self).formfield(form_class=form_class, **kwargs)


class CloudImageField(CloudFileField):
    def formfield(self, **kwargs):
        form_class = kwargs.pop('form_class', None)
        if form_class is None:
            from .forms import CloudImageFormField
            form_class = CloudImageFormField
        return super(CloudImageField, self).formfield(form_class=form_class, **kwargs)


# class Test(models.Model):
#     file = CloudFileField()
