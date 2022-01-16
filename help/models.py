#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
帮助model
"""
from django.db import models
from vadmin.models import VModel
from vadmin import admin_fields


class HelpMenu(VModel):
    """
    帮助菜单（头部）
    """
    label = models.CharField(max_length=512, verbose_name=u"名称")
    key = models.CharField(verbose_name="关键字", max_length=16, blank=True, null=True)
    order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')

    class Meta:
        db_table = "t_help_menu"
        ordering = ['order', 'create_time']
        verbose_name_plural = verbose_name = u"帮助菜单（顶部）"

    def __str__(self):
        return self.label


class HelpMenuLeft(VModel):
    """
    帮助菜单（左边）
    """
    help_menu = admin_fields.ForeignKey(HelpMenu, search_field="label", verbose_name=u'帮助菜单')
    label = models.CharField(max_length=128, verbose_name=u"名称", unique=True)
    key = models.CharField(verbose_name="关键字", max_length=16, blank=True, null=True)
    order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')

    class Meta:
        db_table = "t_help_menu_left"
        ordering = ['order', 'create_time']
        verbose_name_plural = verbose_name = u"帮助菜单（左边）"

    def __str__(self):
        return self.label


class HelpContent(VModel):
    """
    帮助内容
    """
    help_menu_left = admin_fields.ForeignKey(HelpMenuLeft, search_field="label", verbose_name=u'帮助菜单')
    title = models.CharField(max_length=128, blank=True, null=True, verbose_name=u'标题')
    sub_title = models.CharField(max_length=128, blank=True, null=True, verbose_name=u'子标题')
    code = admin_fields.HtmlField(verbose_name="代码", blank=True, null=True)
    content = admin_fields.UEditorField(verbose_name=u"内容", blank=True, null=True)
    # code_title = models.TextField(verbose_name="代码标题", blank=True, null=True)
    link = models.IntegerField(default=1, choices=((1, "URL"), (2, "锚点")), verbose_name=u"链接方式")
    order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')

    class Meta:
        db_table = "t_help_content"
        ordering = ['order', 'create_time']
        verbose_name_plural = verbose_name = u"帮助内容"

    def __str__(self):
        if self.title:
            return self.title
        elif self.sub_title:
            return self.sub_title

        return ""


class HelpWidgetParam(VModel):
    """组件参数"""
    help_menu_left = admin_fields.ForeignKey(HelpMenuLeft, search_field="label", verbose_name=u'帮助菜单')
    name = models.CharField(verbose_name="参数名称", max_length=128, blank=True, null=True)
    desc = models.CharField(verbose_name="参数说明", max_length=512)
    type = models.CharField(verbose_name="参数类型", max_length=32)
    value = models.CharField(verbose_name="参数值说明", max_length=512, blank=True, null=True)
    required = models.BooleanField(verbose_name="必填", default=False)
    default = models.CharField(verbose_name="默认值", blank=True, null=True, max_length=128)
    pc = models.BooleanField(verbose_name="支持PC端", default=True)
    phone = models.BooleanField(verbose_name="支持手机端", default=True)
    order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        db_table = "t_help_widget_param"
        ordering = ['order', 'create_time']
        verbose_name_plural = verbose_name = u"组件参数"

    def __str__(self):
        return self.name


class HelpWidgetEvent(VModel):
    """组件事件"""
    help_menu_left = admin_fields.ForeignKey(HelpMenuLeft, search_field="label", verbose_name=u'帮助菜单')
    name = models.CharField(verbose_name="事件名称", max_length=128)
    desc = models.CharField(verbose_name="事件说明", max_length=512)
    param = models.CharField(verbose_name="提交到后台的参数格式", max_length=512, blank=True, null=True)
    order = models.IntegerField(default=2147483647, db_index=True, verbose_name=u'排序')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        db_table = "t_help_widget_event"
        ordering = ['order', 'create_time']
        verbose_name_plural = verbose_name = u"组件事件"

    def __str__(self):
        return self.name
