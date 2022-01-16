# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111
import os

from django.contrib import admin
from django.forms.models import ModelForm

from file_manager.models import File
from vadmin import common
from vadmin import step
from vadmin import widgets
from vadmin.admin import VModelAdmin


class FileForm(ModelForm):
    v_widgets = {
        'name': widgets.Widget(width=690, height=30),
        'md5': widgets.Widget(width=690),
        'pass_percentage': widgets.Widget(width="100%"),
        'max_number': widgets.Widget(width="100%"),
        'ali_video_id': widgets.Widget(width=690),
        'ali_video_url': widgets.Widget(width=690),
    }


@admin.register(File)
class FileAdmin(VModelAdmin):
    """
    文件表
    """
    form = FileForm
    list_display = ['id', 'name', 'size', 'upload_size', 'ali_upload_size', 'completed', 'type',
                    'duration', 'state', 'update_time', 'create_time']
    list_filter = ['type', 'completed', 'state']
    search_fields = ['id', 'name', 'path', "md5"]
    change_list_config = {"col_width": {"id": 100, "type": 80, "size": 110, "upload_size": 110,
                                        "completed": 70, "duration": 100, "del_flag": 60,
                                        "seconds": 100, "create_time": 160, "update_time": 160,
                                        "state": 200},
                          "sort_fields": ["create_time", ],
                          }
    fieldsets = (
        (None, {'fields': ('name', 'md5', 'type', 'path', 'size', 'upload_size',
                           'completed', 'duration',
                           'first_frame', 'state', 'del_flag')}
         ),

        ("阿里云信息", {'fields': ('ali_upload_size', 'ali_upload_progress',
                              'ali_transcode_progress', 'ali_video_id',
                              'ali_video_url', 'ali_param')}
         ),
    )

    def list_v_size(self, request, obj=None):
        if obj and obj.size:
            return common.format_file_size(obj.size)

    def list_v_upload_size(self, request, obj=None):
        if obj and obj.upload_size:
            return common.format_file_size(obj.upload_size)

    def list_v_ali_upload_size(self, request, obj=None):
        if obj and obj.ali_upload_size:
            return common.format_file_size(obj.ali_upload_size)

    def list_v_path(self, request, obj=None):
        if obj:
            if obj.type == 4:
                return widgets.Image(value=obj.get_url(), width=200, height=200)
            else:
                return obj.get_url()

    def form_v_path(self, request, obj=None):
        if obj:
            if obj.type == 4:
                o_widget = widgets.Image(name="path", value=obj.get_url(), width=200, height=200)
            else:
                url = obj.get_url()
                o_widget = widgets.Upload(name="path", value=url)
        else:
            o_widget = widgets.Upload(name="path")

        return {"name": "文件", "widget": o_widget}

    def form_v_size(self, request, obj=None):
        text = self.list_v_size(request, obj)
        o_widget = widgets.Text(text=text)
        return {"name": "文件大小", "widget": o_widget}

    def form_v_upload_size(self, request, obj=None):
        text = self.list_v_upload_size(request, obj)
        o_widget = widgets.Text(text=text)
        return {"name": "已上传大小", "widget": o_widget}

    def form_v_ali_upload_size(self, request, obj=None):
        text = self.list_v_ali_upload_size(request, obj)
        o_widget = widgets.Text(text=text)
        return {"name": "已上传阿里云大小", "widget": o_widget}

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # return False
        return request.user.is_superuser

    def get_change_form_custom(self, request, obj=None):
        """
        获取form页面自定义功能按钮（在"保存"前面）
        """
        if request.user.is_superuser and obj:
            url = "course.service.test_file_upload/?file_id=%s" % obj.pk
            return widgets.Button(text="更新上传阿里云", step=step.RunScript(url))

        return []

    def delete_model(self, request, obj):
        if obj and obj.path:
            try:
                path = obj.path.path
                os.remove(path)
            except (BaseException,):
                pass
        super().delete_model(request, obj)