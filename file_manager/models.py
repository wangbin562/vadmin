#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
文件model
"""
import os

from django.db import models

from vadmin import admin_fields
from vadmin.models import VModel


class File(VModel):
    """文件表"""
    id = admin_fields.UuidField(verbose_name="ID")
    name = models.TextField(verbose_name="文件名称", blank=True, null=True)
    path = admin_fields.FileField(verbose_name="文件", upload_to='files/%Y-%m-%d', max_length=250,
                                  blank=True, null=True, db_index=True)
    size = models.BigIntegerField(verbose_name=u"文件大小", blank=True, null=True, db_index=True,
                                  help_text="单位：字节")
    upload_size = models.BigIntegerField(verbose_name="已上传大小", blank=True, null=True,
                                         help_text="断点续传使用")
    completed = models.BooleanField(verbose_name="上传完成（本地）", default=False,
                                    help_text="断点续传使用")
    info = models.CharField(verbose_name=u"文件信息", max_length=128, blank=True, null=True)
    md5 = models.CharField(verbose_name="md5信息", max_length=32, blank=True, null=True, db_index=True)
    type = models.IntegerField(verbose_name="文件类型", blank=True, null=True,
                               choices=((1, "文档"), (2, "音频"), (3, "视频"), (4, "图片"), (5, "其它")))
    suffix = models.CharField(verbose_name="文件后缀名", max_length=8, blank=True, null=True)

    # word部分
    dump = models.CharField(verbose_name="dump文件路径", max_length=512, blank=True, null=True,
                            help_text="解析后保存的dump文件路径")
    default_param = models.TextField(verbose_name="模板默认参数", blank=True, null=True)
    param = models.TextField(verbose_name="输入参数", blank=True, null=True, help_text="模板填写参数")

    # 阿里云部分
    ali_upload_size = models.BigIntegerField(verbose_name="已上传阿里云大小", blank=True, null=True,
                                             help_text="断点续传使用")
    ali_upload_progress = models.FloatField(verbose_name="上传阿里进度", blank=True, null=True,
                                            help_text="进度：0-100")
    ali_transcode_progress = models.FloatField(verbose_name="阿里转码进度", blank=True, null=True,
                                               help_text="进度：0-100")
    ali_param = models.TextField(verbose_name="阿里回调参数", blank=True, null=True)
    ali_video_id = models.CharField(verbose_name="阿里VideoId", max_length=128, blank=True, null=True,
                                    db_index=True, help_text="阿里转码成功后才保存")
    ali_video_url = models.TextField(verbose_name="阿里视频播放路径", blank=True, null=True)
    state = models.IntegerField(verbose_name="状态",
                                choices=((6, "上传本地服务器中..."), (0, "上传本地服务器完成"), (1, "上传阿里云中..."),
                                         (7, "上传阿里云失败"), (2, "上传阿里云完成,转码中"), (3, "阿里云转码完成"),
                                         (4, "阿里云转码失败"), (5, "上传阿里云失败"),),
                                default=0)

    duration = models.FloatField(verbose_name="音视频长度（秒）", blank=True, null=True)
    first_frame = models.ImageField(verbose_name="视频文件第一帧图片", max_length=256, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_file"
        verbose_name = verbose_name_plural = u"文件表"
        ordering = ("-update_time",)

    def __str__(self):
        return self.name

    def get_path(self):
        try:
            return os.path.normpath(self.path.path)
        except (BaseException,):
            return self.name

    def get_url(self, is_view=False):
        from utils import global_settings
        try:
            if "/group" in self.path.name:
                url = global_settings.FILE_URL + self.path.name.lstrip("/")  # 兼容老的文件服务器
                if is_view:
                    url = global_settings.FILE_VIEW_URL + url
                return url

            elif "http" in self.path.name:
                return self.path.name

            from django.conf import settings
            if self.path.name:
                return settings.MEDIA_URL + self.path.name

            return ""

        except (BaseException,):
            return ""

    def get_name(self):
        return self.name
