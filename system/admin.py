# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
标准表
"""
from django.forms import ModelForm
from django.contrib import admin
from system.models import AppVersion
from system.models import Dictionary
from vadmin import widgets
from vadmin.admin import VModelAdmin


class AppVersionForm(ModelForm):
    v_widgets = {
        'download_url': widgets.Widget(style={"width": "500px"}),
        'version': widgets.Widget(style={"width": "500px"}),
        'desc': widgets.Input(type="textarea", style={"height": "100px", "width": "500px"}),
    }


@admin.register(AppVersion)
class AppVersionAdmin(VModelAdmin):
    """
    APP版本
    """
    form = AppVersionForm
    list_display = ['client_type', 'download_url', 'version', 'desc', 'force_update',
                    'create_time', 'update_time', 'del_flag']
    list_filter = ['del_flag']  # 过滤字段

    def v_save_after(self, request, old_obj, obj, save_data, update_data,
                     m2m_data, dict_error, inline_data=None, change=True):
        obj.download_url = obj.file.url
        obj.save()


@admin.register(Dictionary)
class DictionaryAdmin(VModelAdmin):
    """
    APP版本
    """
    list_display = ['desc', 'key', 'val', 'begin_time', 'end_time']
