# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
通用model
"""

from django.db import models
from vadmin import admin_fields
from vadmin.models import VModel


class AppVersion(VModel):
    """
    APP版本
    """
    client_type = models.IntegerField(choices=((1, "Android"), (2, "ios")), verbose_name="客户端")
    file = admin_fields.FileField(upload_to='app/', blank=True, null=True, verbose_name='文件')
    download_url = models.CharField(max_length=512, blank=True, null=True, verbose_name="下载路径")
    qr_code = models.FileField(upload_to='images/qr_code', blank=True, null=True, verbose_name="二维码")
    version = models.CharField(max_length=8, verbose_name='版本号')
    desc = models.CharField(max_length=128, verbose_name='说明')
    force_update = models.BooleanField(default=False, verbose_name='强制更新')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_app_version"
        verbose_name_plural = u"APP版本"
        verbose_name = u"APP版本"

    def __str__(self):
        return ""


class Dictionary(VModel):
    """
    字典表
    """
    desc = models.CharField(max_length=256, verbose_name=u'说明')
    key = models.CharField(max_length=56, blank=True, null=True, db_index=True, verbose_name=u'关键字')
    val = models.TextField(blank=True, null=True, verbose_name=u'值')
    val_bool = models.BooleanField(default=False, verbose_name="BOOL值")
    file = admin_fields.FileField(upload_to='file/', blank=True, null=True, verbose_name='文件')
    begin_time = models.DateTimeField(blank=True, null=True, verbose_name=u'开始时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name=u'结束时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_dictionary"
        verbose_name_plural = u"字典参数"
        verbose_name = u"字典参数"

    def __str__(self):
        return ""
