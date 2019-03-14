# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/3/13
"""
from django.shortcuts import redirect
from django.contrib import messages
from jiango.admin.shortcuts import CURDAdmin, edit_view
from jiango.admin.config import ADMIN_PERMISSIONS
from jiango.admin.admin import urlpatterns as system_urlpatterns, sub_menus as system_sub_menus
from .models import File
from .forms import UploadForm


curd_admin = CURDAdmin(
    app_label='admin',
    name='cloud_upload_file',
    verbose_name=u'云文件管理',
    model_class=File,
    display_fields=['id', 'hash', 'size', 'mime', 'width', 'height', 'created_at'],
    search_fields=['hash', 'mime'],
)


@curd_admin.setup_add_view
def add(request, response):
    form = UploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, u'上传完成')
        return redirect('admin:admin:cloud_upload_file')
    return edit_view('admin', request, form, title=u'云文件管理 / 上传')


system_urlpatterns.extend(curd_admin.urlpatterns)

system_sub_menus.extend([
    ('admin:admin:cloud_upload_file', curd_admin.verbose_name, 'fa fa-cloud-upload'),
])

ADMIN_PERMISSIONS.update(curd_admin.permissions)
