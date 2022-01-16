"""
标准表
"""
import importlib
import os
import shell

from django.conf import settings
from django.contrib import admin
from django.forms.models import ModelForm

from vadmin import step
from vadmin import widgets
from vadmin.admin import VModelAdmin
from vadmin_standard.models import Api
from vadmin_standard.models import AppVersion
from vadmin_standard.models import DataDump
from vadmin_standard.models import Dictionary
from vadmin_standard.models import ErrorLog
from vadmin_standard.models import DBDataLog
from vadmin_standard.models import LogicallyDelete
from vadmin_standard.models import OperationLog
from vadmin_standard.models import VersionPatch
from vadmin_standard.models import Environment
from vadmin_standard.models import Todo
from vadmin_standard.models import License


class ApiForm(ModelForm):
    v_widgets = {
        'module': widgets.Widget(width=300),
        'name': widgets.Widget(width=300),
        'desc': widgets.Widget(width=300),
        'method': widgets.Widget(width=300),
        'param': widgets.Widget(width="90%", min_height=200),
        'result': widgets.Widget(width="90%", min_height=200),
    }


@admin.register(Api)
class ApiAdmin(VModelAdmin):
    form = ApiForm
    list_display = ['module', 'name', 'desc', 'method', 'create_time']
    list_v_filter = ['method']
    search_fields = ["name", "desc"]
    exclude = ["order"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_change_list_custom(self, request):
        script1 = "vadmin_standard.service.export_db_2_excel"
        script2 = "vadmin_standard.service.export_db_2_excel"
        script3 = "vadmin_standard.service.export_db_2_excel"
        return [
            widgets.Button(text="导出接口文档"),
            widgets.Button(text="导出数据库文档(Word)", width=180),
            widgets.Button(text="导出数据库文档(Excel)", width=180, step=step.RunScript(script3)),
        ]


class OperationLogForm(ModelForm):
    v_widgets = {
        'operation_desc': widgets.Widget(width="80%", min_height=200),
        'operation_data': widgets.Widget(width="80%", min_height=200),
    }


@admin.register(OperationLog)
class OperationLogAdmin(VModelAdmin):
    """
    操作日志
    """
    form = OperationLogForm
    list_display = ['username', 'ip', 'operation_type', 'operation_desc', 'create_time']
    list_filter = ['operation_type', 'operation_model']
    search_fields = ["username", "operation_desc", "operation_data"]

    change_list_config = {"col_width": {"username": 190, "ip": 130, "operation_type": 70, "create_time": 180,
                                        "operation_model": 180, 'operation_object_id': 160,
                                        "operation_data": 60}}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        return False


class ErrorLogForm(ModelForm):
    v_widgets = {
        'content': widgets.Widget(width="100%")
    }


@admin.register(ErrorLog)
class ErrorLogAdmin(VModelAdmin):
    """
    错误日志
    """
    form = ErrorLogForm
    list_display = ['path', 'level', 'content', 'error_time']
    list_filter = ['level', ]
    change_list_custom = widgets.Button(text="采集",
                                        step=step.RunScript("vadmin_standard.views.format_error_log"))
    change_list_config = {
        "col_width": {"error_time": 180, "path": 120, "level": 80}
    }

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def list_v_error_time(self, request, obj):
        if isinstance(obj.error_time, str):
            return obj.error_time.split(",")[0]

        return obj.error_time.strftime('%Y-%m-%d %H:%M:%S')

    list_v_error_time.short_description = "错误时间"


@admin.register(DBDataLog)
class DBDataLogAdmin(VModelAdmin):
    """
    数据库日志
    """
    list_display = ['app_name', 'verbose_name', 'model_name', 'table_name', 'number', 'create_time']
    search_fields = ['table_name']
    change_list_custom = widgets.Button(text="采集",
                                        step=step.RunScript("vadmin_standard.views.db_data_statistics"))

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class TodoForm(ModelForm):
    v_widgets = {
        'name': widgets.Widget(width="80%"),
        'link': widgets.Widget(width="80%"),
        'desc': widgets.Input(input_type="textarea", height=100, width="80%"),
    }


@admin.register(Todo)
class TodoAdmin(VModelAdmin):
    """
    代办事项
    """
    form = TodoForm
    list_display = ['user_id', 'username', 'name', 'desc', 'complete', 'create_time']
    list_filter = ['complete']  # 过滤字段
    search_fields = ["user_id", "username", "name"]
    change_list_config = {"col_width": {"user_id": 120, "username": 200, "complete": 65, "create_time": 180}}

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


class AppVersionForm(ModelForm):
    v_widgets = {
        'download_url': widgets.Widget(width="90%"),
        'version': widgets.Widget(width=500),
        'desc': widgets.Input(input_type="textarea", height=100, width=500),
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

    def save_after(self, request, old_obj, obj, save_data, update_data,
                   m2m_data, dict_error, inline_data=None, change=True):
        try:
            if obj.file:
                obj.download_url = obj.file.name
                obj.save()
        except (BaseException,):
            pass


@admin.register(Dictionary)
class DictionaryAdmin(VModelAdmin):
    """
    字典
    """
    list_display = ['desc', 'key', 'val', 'begin_time', 'end_time']


@admin.register(LogicallyDelete)
class LogicallyDeleteAdmin(VModelAdmin):
    """
    逻辑删除配置
    """
    list_display = ['app_label', 'model_name', 'field_name', 'enable', 'create_time']
    list_filter = ['enable']

    def save_before(self, request, old_obj, data, dict_error, inline_data=None):
        data['app_label'] = data['app_label'].lower()
        data['model_name'] = data['model_name'].lower()


@admin.register(DataDump)
class DataDumpAdmin(VModelAdmin):
    """
    数据转储
    """
    list_display = ['app_label', 'model_name', 'max_number', 'order_field', 'max_day', 'enable', 'create_time']
    list_filter = ['enable']

    def save_after(self, request, old_obj, obj, save_data, update_data,
                   m2m_data, dict_error, inline_data=None, change=True):
        if not save_data["max_number"] and save_data["max_day"] and not save_data["order_field"]:
            dict_error["order_field"] = "保存最长天数情况下比较字段不能为空！"


@admin.register(VersionPatch)
class VersionPatchAdmin(VModelAdmin):
    """
    版本升级
    """
    list_display = ['version', 'desc', 'enable', 'create_time']
    list_filter = ['enable']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_after(self, request, old_obj, obj, save_data, update_data,
                   m2m_data, dict_error, inline_data=None, change=True):
        if update_data and obj.enable:
            file_path = os.path.join(settings.MEDIA_ROOT, "script", "__init__.py")
            if not os.path.exists(file_path):
                fh = open(file_path, "w")
                fh.write("# !/usr/bin/python")
                fh.close()

            file_name = os.path.splitext(os.path.split(obj.upgrade.name)[1])[0]
            o_module = importlib.import_module("media.script.%s" % file_name)


class LicenseForm(ModelForm):
    v_widgets = {
        'code': widgets.Widget(width="90%", max_height=300),
        'desc': widgets.Widget(width="90%", max_height=300),
        'license': widgets.Widget(width="90%", max_height=300),
    }


@admin.register(License)
class LicenseAdmin(VModelAdmin):
    """
    License
    """
    form = LicenseForm
    list_display = ['domain', 'port', 'expire_date', 'code', 'desc', 'license', 'create_time']
    readonly_v_fields = ['code']

    def save_before(self, request, old_obj, data, dict_error, inline_data=None):
        import uuid
        import socket
        address = hex(uuid.getnode())[2:]
        data['code'] = "%s|%s|%s|%s|%s" % (data["domain"], data["port"], socket.gethostname(),
                                           ':'.join(address[i:i + 2] for i in range(0, len(address), 2)),
                                           data["expire_date"] or "")


class EnvironmentForm(ModelForm):
    v_widgets = {
        'cpu': widgets.Widget(width="90%", height=200, max_height=300),
        'memory': widgets.Widget(width="90%", height=200, max_height=300),
        'hard_disk': widgets.Widget(width="90%", height=200, max_height=300),
        'last_error': widgets.Widget(width="90%", height=200, max_height=300),
    }


@admin.register(Environment)
class EnvironmentAdmin(VModelAdmin):
    """
    环境检测
    """
    form = EnvironmentForm
    list_display = ['cpu', 'memory', 'hard_disk', 'update_time']

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_object(self, request, object_id, from_field=None):
        """根据ID获取对象"""
        obj = super().get_object(request, object_id, from_field)
        try:
            r = shell.shell("df -h")
            obj.hard_disk = "\r\n".join(r.output())
        except (BaseException,):
            pass

        try:
            r = shell.shell("sar -u 1 1")
            obj.cpu = "\r\n".join(r.output())
        except (BaseException,):
            # try:
            #     r = shell.shell("top -n 1")
            #     obj.cpu = "\r\n".join(r.output())
            # except (BaseException,):
            #     pass
            pass

        try:
            r = shell.shell("free -t -m")
            obj.memory = "\r\n".join(r.output())
        except (BaseException,):
            # try:
            #     r = shell.shell("top -n 1")
            #     obj.memory = "\r\n".join(r.output())
            # except (BaseException,):
            #     pass
            pass

        try:
            path = os.path.join(settings.BASE_DIR, "logs")
            path = os.path.abspath(path)
            for file_name in os.listdir(path):
                if file_name.find(".log") == (len(file_name) - 4):
                    file_path = os.path.join(path, file_name)
                    file_path = os.path.abspath(file_path)
                    buf = open(file_path, "rb").read()
                    lst_item = buf.split(b"[ERROR]")
                    if lst_item:
                        text1 = str(lst_item[0], encoding="utf-8")
                        text2 = str(lst_item[-1], encoding="utf-8")
                        lst_error = [text1.rsplit("\n", 1)[-1], text2.rsplit("\n", 1)[-1], "[ERROR]"]
                        item2 = text2.split("[INFO]")[0].split("[WARNING]")[0].split("[DEBUG]")[0]
                        sub = item2.rsplit("\n", 1)
                        lst_error.append(sub[0])
                        obj.last_error = "".join(lst_error)
        except (BaseException,):
            pass

        obj.save()
        return obj
