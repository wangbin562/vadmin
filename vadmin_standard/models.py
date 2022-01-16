# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
通用model
"""

from django.db import models
from vadmin import admin_fields
from vadmin.models import VModel


class Api(VModel):
    """接口"""
    module = models.CharField(verbose_name="module", max_length=128, db_index=True)
    name = models.CharField(verbose_name="名称", max_length=64, db_index=True)
    desc = models.CharField(verbose_name="说明", max_length=256, blank=True, null=True)
    method = models.CharField(verbose_name="方式", max_length=8, default="GET")
    param = models.TextField(verbose_name="参数", blank=True, null=True)
    result = models.TextField(verbose_name="返回值", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_api"
        verbose_name = verbose_name_plural = u"接口"
        ordering = ("order", "-create_time")
        unique_together = ("module", "name")

    def __str__(self):
        return ""


class OperationLog(VModel):
    """
    操作日志（可以在admin中配置）
    """
    id = admin_fields.UuidField(max_length=32, primary_key=True, verbose_name="ID")
    user_id = models.CharField(db_index=True, verbose_name=u"用户ID", max_length=32)
    username = models.CharField(max_length=128, blank=True, null=True, db_index=True, verbose_name=u"用户名称")
    ip = models.CharField(verbose_name=u"访问IP", max_length=16, blank=True, null=True)
    # log_type = models.CharField(max_length=128, blank=True, null=True, db_index=True, verbose_name=u"日志类型")
    operation_type = models.IntegerField(default=1, choices=((1, u"新增"), (2, u"删除"), (3, u"修改")), verbose_name=u"操作类型")
    # operation_object = models.TextField(blank=True, null=True, verbose_name=u"操作对象")
    operation_model = models.CharField(max_length=128, blank=True, null=True, verbose_name="操作的Model",
                                       help_text="格式：app_label.model.name")
    operation_object_id = models.CharField(max_length=32, db_index=True, blank=True, null=True, verbose_name=u"操作对象ID")
    # operation_sub_object = models.TextField(blank=True, null=True, verbose_name=u"操作子对象")
    # operation_sub_object_id = models.CharField(max_length=32, db_index=True, blank=True, null=True,
    #                                            verbose_name=u"操作子对象ID")
    # operation_sub_model = models.IntegerField(blank=True, null=True, verbose_name="操作的Model",
    #                                           help_text="格式：app_label.model.name")
    operation_desc = models.TextField(verbose_name=u"操作详情", blank=True, null=True)
    operation_data = models.TextField(verbose_name=u"操作数据", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u"创建时间")

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_operation_log"
        verbose_name = verbose_name_plural = u"操作日志"
        ordering = ("-create_time",)

    def __str__(self):
        return str(self.pk)


class ErrorLog(VModel):
    """
    错误日志
    """
    path = models.CharField(verbose_name="文件", max_length=126)
    level = models.IntegerField(verbose_name="错误级别", choices=((1, "ERROR"), (2, "WARNING")), default=1)
    content = models.TextField(verbose_name="错误内容", blank=True, null=True)
    error_time = models.CharField(verbose_name="错误时间", max_length=32, db_index=True, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_error_log"
        verbose_name = verbose_name_plural = u"错误日志"
        ordering = ("-error_time",)

    def __str__(self):
        return ""


class DBDataLog(VModel):
    """
    数据库日志
    """
    app_name = models.CharField(verbose_name="应用名称", max_length=256, blank=True, null=True)
    verbose_name = models.CharField(verbose_name="表说明", max_length=512)
    model_name = models.CharField(verbose_name="类名", max_length=256)
    table_name = models.CharField(verbose_name="表名", max_length=256, db_index=True)
    number = models.IntegerField(verbose_name="条数")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_db_data_log"
        verbose_name = verbose_name_plural = u"数据库日志"
        ordering = ("-create_time",)

    def __str__(self):
        return self.table_name


class CommonLink(VModel):
    """
    常用链接
    """
    id = admin_fields.UuidField(max_length=32, primary_key=True, verbose_name="ID")
    user_id = models.CharField(max_length=32, db_index=True, verbose_name=u"用户ID",
                               blank=True, null=True, help_text="为空默认所有人都有此链接")
    name = models.CharField(verbose_name=u'链接名称', max_length=64, db_index=True)
    link = models.CharField(verbose_name=u'链接', max_length=512)
    background_color = models.CharField(max_length=16, blank=True, null=True, verbose_name=u'背景颜色')
    is_del = models.BooleanField(verbose_name="是否可以删除", default=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_common_link"
        verbose_name_plural = u"常用链接"
        verbose_name = u"常用链接"

    def __str__(self):
        return self.name


class Todo(VModel):
    """
    代办事项
    """
    id = admin_fields.UuidField(max_length=32, primary_key=True, verbose_name="ID")
    user_id = models.CharField(max_length=32, db_index=True, verbose_name=u"用户ID")
    username = models.CharField(max_length=128, blank=True, null=True, db_index=True, verbose_name=u"用户名称")
    # title = models.CharField(max_length=32, verbose_name=u"标题")
    object_id = models.CharField(verbose_name=u"对象ID", max_length=32, db_index=True, blank=True, null=True)
    key = models.CharField(verbose_name=u"关键字", max_length=32, db_index=True, blank=True, null=True)
    name = models.CharField(verbose_name=u"名称", max_length=64, blank=True, null=True)
    desc = models.CharField(verbose_name=u"说明", max_length=256, blank=True, null=True)
    link = models.CharField(verbose_name=u"链接", max_length=256, blank=True, null=True)
    # opera = models.CharField(max_length=32, verbose_name=u"操作")
    complete = models.BooleanField(default=False, verbose_name=u"完成")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_todo"
        verbose_name = verbose_name_plural = u"代办事项"
        ordering = ("-create_time",)

    def __str__(self):
        if self.name:
            return self.name
        elif self.desc:
            return self.desc
        elif self.link:
            return self.link

        return str(self.id)


class AppVersion(VModel):
    """
    APP版本
    """
    id = admin_fields.UuidField(verbose_name="ID")
    client_type = models.IntegerField(choices=((1, "Android"), (2, "ios")), verbose_name="客户端")
    file = admin_fields.FileField(upload_to='app/', blank=True, null=True, verbose_name='文件')
    download_url = models.CharField(max_length=512, blank=True, null=True, verbose_name="下载路径")
    qr_code = models.FileField(upload_to='images/qr_code', blank=True, null=True, verbose_name="二维码")
    version = models.CharField(max_length=8, verbose_name='版本号')
    desc = models.CharField(verbose_name='说明', max_length=128, blank=True, null=True)
    force_update = models.BooleanField(default=False, verbose_name='强制更新')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_app_version"
        verbose_name_plural = u"APP版本"
        verbose_name = "APP版本"

    def __str__(self):
        return ""


class Dictionary(VModel):
    """
    字典表
    """
    id = admin_fields.UuidField(verbose_name="ID")
    desc = models.CharField(verbose_name=u'说明', max_length=256)
    key = models.CharField(verbose_name=u'关键字', max_length=56, blank=True, null=True, db_index=True)
    val = models.TextField(verbose_name=u'值', blank=True, null=True)
    val_bool = models.BooleanField(verbose_name="BOOL值", default=False)
    begin_val = models.CharField(verbose_name="开始值（或及格值）", max_length=256, blank=True, null=True)
    end_val = models.CharField(verbose_name="结束值（或总值）", max_length=256, blank=True, null=True)
    file = admin_fields.FileField(verbose_name='文件', blank=True, null=True)
    begin_time = models.DateTimeField(blank=True, null=True, verbose_name=u'开始时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name=u'结束时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_dictionary"
        verbose_name_plural = u"字典参数"
        verbose_name = "字典参数"

    def __str__(self):
        return ""


class LogicallyDelete(VModel):
    """
    逻辑删除配置
    """
    id = admin_fields.UuidField(verbose_name="ID")
    app_label = models.CharField(verbose_name="app名称", max_length=64, blank=True, null=True)
    model_name = models.CharField(verbose_name="model名称", max_length=64)
    field_name = models.CharField(verbose_name="字段", max_length=64, default="del_flag")
    enable = models.BooleanField(verbose_name='启用', default=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_logically_delete"
        verbose_name = verbose_name_plural = u"逻辑删除配置"
        ordering = ("-create_time",)

    def __str__(self):
        return ""


class DataDump(VModel):
    """数据转储配置"""
    id = admin_fields.UuidField(verbose_name="ID")
    app_label = models.CharField(verbose_name="app名称", max_length=64, blank=True, null=True)
    model_name = models.CharField(verbose_name="model名称", max_length=64)
    order_field = models.CharField(verbose_name="排序或比较字段字段", max_length=128, blank=True, null=True,
                                   help_text="多个用,分割")
    max_number = models.IntegerField(verbose_name="保存最大条数", blank=True, null=True)
    max_day = models.IntegerField(verbose_name="保存最长天数", blank=True, null=True)
    enable = models.BooleanField(verbose_name='启用', default=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_data_dump"
        verbose_name = verbose_name_plural = u"数据转储配置"
        ordering = ("-create_time",)

    def __str__(self):
        return ""


class VersionPatch(VModel):
    """版本补丁"""
    version = models.FloatField(verbose_name="版本号", max_length=64)
    desc = models.CharField(verbose_name="升级说明", max_length=256, blank=True, null=True)
    upgrade = admin_fields.FileField(verbose_name="升级脚本文件", upload_to="script")
    enable = models.BooleanField(verbose_name='启用', default=False)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_version_patch"
        verbose_name = verbose_name_plural = u"版本升级"
        ordering = ("-create_time",)

    def __str__(self):
        return str(self.version)


class License(VModel):
    """license管理"""
    domain = models.CharField(verbose_name="域名", max_length=64, help_text="实际使用,有可能是IP地址")
    port = models.IntegerField(verbose_name="端口")
    expire_date = models.DateField(verbose_name="到期时间", blank=True, null=True,
                                   help_text="为空永远使用")
    desc = models.CharField(verbose_name="说明", max_length=256, blank=True, null=True)
    code = models.TextField(verbose_name="机器码", blank=True, null=True,
                            help_text="代码自动获取, 生成license基础数据. 如果修改了域名或端口, 要重新生成license")
    license = models.TextField(verbose_name="license", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'删除')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_license"
        verbose_name = verbose_name_plural = "license管理"

    def __str__(self):
        return str(self.code)


class Environment(VModel):
    """环境检测"""
    cpu = models.TextField(verbose_name="CPU使用情况", blank=True, null=True)
    memory = models.TextField(verbose_name="内存使用情况", blank=True, null=True)
    hard_disk = models.TextField(verbose_name="硬盘使用情况", blank=True, null=True)
    last_error = models.TextField(verbose_name="最后错误日志", blank=True, null=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta(object):  # pylint: disable=C0111
        db_table = "t_v_environment"
        verbose_name = verbose_name_plural = "环境检测"

    def __str__(self):
        return ""


# class DocumentDirectory(VModel):
#     """文档目录"""
#     name = models.TextField(verbose_name="目录名称")
#     parent = admin_fields.ForeignKey(verbose_name="父级", to="self", blank=True, null=True)
#     level = models.IntegerField(verbose_name="目录级别", blank=True, null=True)
#     content = models.TextField(verbose_name="内容", blank=True, null=True)
#     file = admin_fields.FileForeignKey(verbose_name="视频", to=File, blank=True, null=True)
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
#     update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
#     del_flag = models.BooleanField(default=False, verbose_name=u'删除')
#
#     class Meta(object):  # pylint: disable=C0111
#         db_table = "t_v_document_directory"
#         verbose_name_plural = u"文档目录"
#         verbose_name = "文档目录"
#
#     def __str__(self):
#         return ""
#
#
# class ElectronicSignature(VModel):
#     """电子签章"""
#     pass


"""导出API, 在API界面实现"""
"""导出数据库设计，在API界面实现"""
